/* Search Ops dashboard. Reads the canonical analysis JSON (read-only) and stores operator
   feedback in this browser's localStorage. No model call, no account connection.
   All operator-entered text is rendered with textContent (never innerHTML). */
(function () {
  'use strict';

  const ANALYSIS_URL = '../output/canonical/search_ops_analysis.json';
  const FEEDBACK_FORMAT = 'search_ops_operator_feedback';
  const FEEDBACK_FORMAT_VERSION = '1.0';
  const DECISIONS = ['', 'keep', 'expand', 'isolate', 'reduce_exposure', 'negative', 'measure_on_leads', 'hold'];
  const DECISION_LABELS = { '': '— not decided —', keep: 'Keep', expand: 'Expand', isolate: 'Isolate', reduce_exposure: 'Reduce exposure', negative: 'Negative', measure_on_leads: 'Measure on leads', hold: 'Hold' };
  const FACT_STATUS = [['unverified_assumption', 'Unverified assumption'], ['confirmed_fact', 'Confirmed fact']];
  const QA_TO = ['product', 'data', 'sales', 'marketing', 'account owner', 'operator', 'other'];

  const state = { a: null, identity: null, storageKey: null, feedback: null, selected: null, saveTimer: null };

  // ---------- DOM helpers ----------
  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) for (const k of Object.keys(attrs)) {
      const v = attrs[k];
      if (v === null || v === undefined) continue;
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else if (k === 'html') throw new Error('innerHTML is not allowed');
      else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
      else if (k === 'checked' || k === 'selected' || k === 'disabled' || k === 'hidden') node[k] = !!v;
      else node.setAttribute(k, v);
    }
    if (children) for (const c of [].concat(children)) {
      if (c === null || c === undefined || c === false) continue;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return node;
  }
  const $ = (sel) => document.querySelector(sel);
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); return node; }

  // ---------- formatting (values are decimal strings; null = unknown) ----------
  const isNum = (v) => v !== null && v !== undefined && v !== '' && !Number.isNaN(Number(v));
  function money(v, d) { if (!isNum(v)) return '—'; return '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: d === undefined ? 2 : d, maximumFractionDigits: d === undefined ? 2 : d }); }
  function count(v) { if (!isNum(v)) return '—'; return Number(v).toLocaleString('en-US', { maximumFractionDigits: 4 }); }
  function pct(v, d) { if (!isNum(v)) return '—'; return (Number(v) * 100).toFixed(d === undefined ? 1 : d) + '%'; }
  function times(v) { if (!isNum(v)) return '—'; return Number(v).toFixed(2) + 'x'; }
  function cmpClass(status) { return status === 'above' ? 'above' : status === 'below' ? 'below' : ''; }

  // ---------- feedback model ----------
  function emptyTermFeedback() {
    return { missing_data_notes: [], product_questions_and_answers: [], operator_insight: { text: '', status: 'unverified_assumption' }, final_decision: '', decision_rationale: '' };
  }
  function emptyFeedback() {
    return { format: FEEDBACK_FORMAT, format_version: FEEDBACK_FORMAT_VERSION, analysis_identity: state.identity, exported_at: null, posture_selection: '', global: emptyTermFeedback(), terms: {} };
  }
  function termFeedback(tid) {
    if (!state.feedback.terms[tid]) state.feedback.terms[tid] = emptyTermFeedback();
    return state.feedback.terms[tid];
  }
  function identityOf(a) {
    return {
      artifact: a.artifact, schema_version: a.schema_version, review_basis: a.versions.review_basis,
      step1_search_terms_sha256: a.sources.step1.inputs.search_terms.sha256,
      review_authoring_sha256: a.sources.review.authoring_sha256,
    };
  }
  function sameIdentity(x, y) {
    return !!x && !!y && ['artifact', 'schema_version', 'review_basis', 'step1_search_terms_sha256', 'review_authoring_sha256'].every((k) => x[k] === y[k]);
  }
  const isStr = (v) => typeof v === 'string';
  function validateFeedback(obj) {
    const errs = [];
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return ['Not a JSON object.'];
    if (obj.format !== FEEDBACK_FORMAT) errs.push('format must be "' + FEEDBACK_FORMAT + '".');
    if (obj.format_version !== FEEDBACK_FORMAT_VERSION) errs.push('format_version must be "' + FEEDBACK_FORMAT_VERSION + '".');
    if (!sameIdentity(obj.analysis_identity, state.identity)) errs.push('analysis_identity does not match this dataset/analysis (' + state.identity.review_basis + ').');
    if (obj.posture_selection !== undefined && !['', 'scale', 'maintain_efficiency'].includes(obj.posture_selection)) errs.push('posture_selection invalid.');
    if (!obj.terms || typeof obj.terms !== 'object' || Array.isArray(obj.terms)) errs.push('terms must be an object keyed by term_id.');
    else {
      const known = new Set(state.a.terms.map((t) => t.term_id));
      for (const tid of Object.keys(obj.terms)) {
        if (!known.has(tid)) { errs.push('unknown term_id ' + tid + '.'); continue; }
        errs.push(...validateTermFeedback(obj.terms[tid], tid));
      }
    }
    if (obj.global !== undefined) errs.push(...validateTermFeedback(obj.global, 'global'));
    return errs;
  }
  function validateTermFeedback(t, label) {
    const errs = [];
    if (!t || typeof t !== 'object') return [label + ': must be an object.'];
    if (!Array.isArray(t.missing_data_notes) || !t.missing_data_notes.every((n) => n && isStr(n.text) && isStr(n.status))) errs.push(label + ': missing_data_notes malformed.');
    if (!Array.isArray(t.product_questions_and_answers) || !t.product_questions_and_answers.every((q) => q && isStr(q.question) && isStr(q.answer) && isStr(q.to) && isStr(q.answer_status))) errs.push(label + ': product_questions_and_answers malformed.');
    if (!t.operator_insight || !isStr(t.operator_insight.text) || !isStr(t.operator_insight.status)) errs.push(label + ': operator_insight malformed.');
    if (!(t.final_decision === null || (isStr(t.final_decision) && DECISIONS.includes(t.final_decision)))) errs.push(label + ': final_decision invalid.');
    if (!isStr(t.decision_rationale)) errs.push(label + ': decision_rationale must be a string.');
    return errs;
  }
  function loadFeedback() {
    try {
      const raw = localStorage.getItem(state.storageKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (validateFeedback(parsed).length === 0) { parsed.terms = parsed.terms || {}; parsed.global = parsed.global || emptyTermFeedback(); return parsed; }
      }
    } catch (e) { /* fall through to empty */ }
    return emptyFeedback();
  }
  function saveFeedback(immediate) {
    clearTimeout(state.saveTimer);
    const doSave = () => {
      try {
        localStorage.setItem(state.storageKey, JSON.stringify(state.feedback));
        setSaveStatus('Saved on this browser only · ' + new Date().toLocaleTimeString());
      } catch (e) { setSaveStatus('Could not save to this browser (storage unavailable).'); }
      renderDecisionColumns();
    };
    if (immediate) doSave(); else state.saveTimer = setTimeout(doSave, 300);
  }
  function setSaveStatus(msg) { $('#save-status').textContent = msg; }
  function hasAnyFeedback(fb) {
    const any = (t) => t && (t.missing_data_notes.length || t.product_questions_and_answers.length || t.operator_insight.text || t.final_decision || t.decision_rationale);
    return any(fb.global) || Object.values(fb.terms).some(any);
  }

  // ---------- export / import ----------
  function exportFeedback() {
    const payload = exportPayload();
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = el('a', { href: URL.createObjectURL(blob), download: 'operator_feedback.json' });
    document.body.appendChild(a); a.click(); a.remove();
    showImportMessage('Exported operator_feedback.json. Save it into the project (e.g. operator/) and ask Claude Code for a reanalysis that consumes it.', 'ok');
  }
  function importFeedbackFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
      let parsed;
      try { parsed = JSON.parse(String(reader.result)); } catch (e) { return showImportMessage('Import rejected: file is not valid JSON. Existing notes were not changed.', 'error'); }
      const errs = validateFeedback(parsed);
      if (errs.length) return showImportMessage('Import rejected: ' + errs.join(' ') + ' Existing notes were not changed.', 'error');
      if (hasAnyFeedback(state.feedback) && !window.confirm('Replace the notes currently saved on this browser with the imported file?')) {
        return showImportMessage('Import cancelled. Existing notes were not changed.', '');
      }
      applyValidatedFeedback(parsed);
      showImportMessage('Imported operator feedback for ' + Object.keys(parsed.terms).length + ' term(s).', 'ok');
    };
    reader.onerror = () => showImportMessage('Import rejected: could not read the file.', 'error');
    reader.readAsText(file);
  }
  function applyValidatedFeedback(parsed) {
    state.feedback = { format: FEEDBACK_FORMAT, format_version: FEEDBACK_FORMAT_VERSION, analysis_identity: state.identity, exported_at: null, posture_selection: parsed.posture_selection || '', global: parsed.global || emptyTermFeedback(), terms: parsed.terms };
    saveFeedback(true);
    applyPostureToControls();
    renderAll();
  }
  function exportPayload() {
    const payload = JSON.parse(JSON.stringify(state.feedback));
    payload.exported_at = new Date().toISOString();
    payload.note = 'Operator feedback for Search Ops. Human decisions only; nothing was executed. Apply only to the analysis named in analysis_identity.';
    return payload;
  }
  function showImportMessage(msg, kind) {
    const box = $('#import-message');
    box.className = 'notice' + (kind ? ' ' + kind : '');
    box.textContent = msg; box.hidden = false;
  }

  // ---------- posture ----------
  function posture() { return state.feedback.posture_selection || ''; }
  function postureLabel(p) { return p === 'scale' ? 'Scale' : p === 'maintain_efficiency' ? 'Maintain efficiency' : 'Not selected'; }
  function applyPostureToControls() {
    document.querySelectorAll('input[name=posture]').forEach((r) => { r.checked = r.value === posture(); });
  }
  function onPostureChange(e) {
    state.feedback.posture_selection = e.target.value;
    saveFeedback(true);
    renderPostureNote(); renderBranchTable(); if (state.selected) renderDetail();
  }
  function renderPostureNote() {
    const p = posture();
    $('#posture-note').textContent = p
      ? 'Showing the "' + postureLabel(p) + '" branch saved in review ' + state.a.versions.review_basis.replace('step2-review-', '') + '. Your selection is stored with your notes on this browser; the canonical baseline still records posture as not selected.'
      : 'No posture selected. Both branches are shown per term; the analysis does not choose for you.';
  }

  // ---------- view: Business Insights ----------
  function renderLevels() {
    const s = state.a.metrics.scope_levels;
    const cta = $('#review-terms-link');
    cta.addEventListener('click', (e) => { e.preventDefault(); showTab('terms'); if (!state.selected) selectTerm(state.a.terms[0].term_id); $('#terms-title').focus(); window.scrollTo({ top: 0 }); }, { once: false });
    const paid = state.a.metrics.channels.find((c) => c.is_aggregate === 'true');
    const cards = [
      { label: 'Total paid (aggregate of 7 channels, Q2 label)', spend: paid.q2_spend, subs: paid.q2_subs, cps: paid.q2_cost_per_sub_recomputed, note: 'supplied ' + money(paid.q2_cost_per_sub_supplied) + ' · differs from recomputed; cause unknown', cls: '' },
      { label: 'All Google Non-Brand (Q2 label)', spend: s.all_google_non_brand.spend, subs: s.all_google_non_brand.paid_sub, cps: s.all_google_non_brand.cost_per_sub_recomputed, note: 'period alignment with the scope unverified', cls: '' },
      { label: 'Scope: Non-Brand "ai app builder" (last quarter)', spend: s.scope.spend, subs: s.scope.paid_sub, cps: s.scope.cost_per_sub_recomputed, note: 'observed benchmark, not a target · supplied ' + money(s.scope.cost_per_sub_supplied), cls: 'level-2' },
      { label: 'Nine-term sample', spend: s.sample.cost, subs: s.sample.paid_sub, cps: s.sample.cost_per_sub_recomputed, note: pct(s.sample.spend_coverage_of_scope_actual) + ' of scope spend (reported ~' + pct(s.sample.spend_coverage_of_scope_reported, 0) + ') · describes only these rows', cls: '' },
    ];
    clear($('#level-cards')).append(...cards.map((c) => el('div', { class: 'kpi ' + c.cls }, [
      el('span', { text: c.label }),
      el('strong', { text: money(c.cps) + ' / sub' }),
      el('small', { text: money(c.spend, 0) + ' spend · ' + count(c.subs) + ' subs' }),
      el('small', { text: c.note }),
    ])));
    const r = state.a.account_context;
    clear($('#reference-card')).append(
      el('p', { class: 'eyebrow', text: 'TWO DIFFERENT REFERENCE POINTS' }),
      el('h2', { text: 'Allowable vs observed benchmark' }),
      el('div', { class: 'detail-numbers' }, [
        el('div', {}, [el('span', { text: 'Non-Brand allowable (operator target)' }), el('strong', { text: money(r.allowable.non_brand_cost_per_sub) }), el('small', { class: 'small', text: 'source: ' + r.allowable.source })]),
        el('div', {}, [el('span', { text: 'Scope cost/sub (observed benchmark)' }), el('strong', { text: money(r.performance_benchmark.scope_cost_per_sub_recomputed) }), el('small', { class: 'small', text: 'source: step 1 recomputation (520,000 / 3,100)' })]),
        el('div', {}, [el('span', { text: 'Remainder of scope (by subtraction)' }), el('strong', { text: money(s.remainder.cost_per_sub) }), el('small', { class: 'small', text: 'no individual terms known' })]),
      ]),
      el('p', { class: 'small', text: 'The allowable is the target the brief supplies; the benchmark is what the scope actually ran at. Reaching the allowable is not financial break-even: margin and customer value are unknown.' }),
    );
  }
  function renderChannels() {
    const body = clear($('#channel-table tbody'));
    for (const c of state.a.metrics.channels) {
      const agg = c.is_aggregate === 'true';
      const ratioCls = isNum(c.cost_per_sub_to_allowable_ratio) ? (Number(c.cost_per_sub_to_allowable_ratio) > 1 ? 'above' : 'below') : '';
      body.appendChild(el('tr', { class: agg ? 'aggregate' : '' }, [
        el('td', { text: agg ? '—' : c.rank_by_q2_spend }),
        el('td', { class: 'left' }, [c.channel, agg ? el('small', { text: 'aggregate · excluded from ranking, shares and sums' }) : null]),
        el('td', { text: money(c.q2_spend, 0) }), el('td', { text: count(c.q2_subs) }),
        el('td', { text: money(c.q2_cost_per_sub_recomputed) }),
        el('td', {}, [money(c.q2_cost_per_sub_supplied), c.q2_cost_per_sub_matches_supplied === 'false' ? el('small', { class: 'above', text: 'mismatch > $0.005' }) : null]),
        el('td', {}, [money(c.q1_cost_per_sub_supplied), el('small', { text: 'not verifiable' })]),
        el('td', { text: isNum(c.allowable_cost_per_sub) ? money(c.allowable_cost_per_sub, 0) : 'unavailable' }),
        el('td', { class: ratioCls, text: isNum(c.cost_per_sub_to_allowable_ratio) ? times(c.cost_per_sub_to_allowable_ratio) : '—' }),
        el('td', { text: agg ? '—' : pct(c.share_of_paid_spend) }),
      ]));
    }
    clear($('#channel-observations')).append(...state.a.insights.channel_observations.map((o) => el('li', { text: o.observation })));
  }
  function renderPatterns() {
    const box = clear($('#patterns'));
    for (const p of state.a.insights.patterns) {
      box.appendChild(el('details', {}, [
        el('summary', {}, [el('span', { text: p.id + ' · ' + p.title })]),
        el('div', { class: 'body' }, [
          el('h4', {}, [el('span', { class: 'pill fact', text: 'observed · fact' })]),
          el('p', { class: 'detail-note', text: p.observed }),
          el('div', {}, [el('span', { class: 'pill', text: 'supporting' }), ...p.supporting.map((t) => el('span', { class: 'pill', text: t }))]),
          el('div', { style: 'margin-top:6px' }, [el('span', { class: 'pill warn', text: 'counterexamples' }), ...(p.counterexamples.length ? p.counterexamples.map((t) => el('span', { class: 'pill', text: t })) : [el('span', { class: 'pill na', text: 'none in the sample' })])]),
          el('h4', {}, [el('span', { class: 'pill hyp', text: 'possible explanations · hypotheses, not ranked' })]),
          el('ul', {}, p.explanations.map((x) => el('li', { text: x }))),
          el('h4', { text: 'What would distinguish them' }),
          el('p', { class: 'detail-note muted-text', text: p.distinguishing_evidence }),
        ]),
      ]));
    }
  }
  function renderBranchTable() {
    const p = posture();
    $('#branch-col').textContent = p ? 'Branch: ' + postureLabel(p) : 'Branches (no posture selected)';
    const body = clear($('#branch-table tbody'));
    for (const t of state.a.terms) {
      const b = t.conditional_recommendation.branches;
      body.appendChild(el('tr', {}, [
        el('td', { class: 'left' }, [el('strong', { text: t.search_term })]),
        el('td', { class: cmpClass(t.comparison.vs_allowable.status), text: money(t.metrics.cost_per_sub_recomputed) }),
        el('td', { class: 'wrap', text: t.conditional_recommendation.lean }),
        el('td', { class: 'wrap' }, p ? [b[p]] : [el('div', {}, [el('span', { class: 'pill', text: 'scale' }), ' ' + b.scale]), el('div', { style: 'margin-top:6px' }, [el('span', { class: 'pill', text: 'maintain efficiency' }), ' ' + b.maintain_efficiency])]),
      ]));
    }
  }

  // ---------- view: Search Terms ----------
  function renderTermTable() {
    const body = clear($('#term-table tbody'));
    for (const t of state.a.terms) {
      const m = t.metrics;
      body.appendChild(el('tr', { class: t.term_id === state.selected ? 'selected' : '', 'data-tid': t.term_id }, [
        el('td', {}, [el('button', { class: 'term-btn', type: 'button', 'aria-label': 'Select ' + t.search_term, onclick: () => selectTerm(t.term_id) }, [t.search_term]), el('small', { text: t.match_type_source + ' match (triggering type) · #' + t.rank_by_cost + ' by cost' })]),
        el('td', { text: money(m.cost, 0) }), el('td', { text: count(m.signup) }), el('td', { text: count(m.paid_sub) }),
        el('td', { text: pct(m.paid_sub_per_signup) }),
        el('td', { text: money(m.cost_per_sub_recomputed) }),
        el('td', { class: cmpClass(t.comparison.vs_allowable.status), text: times(t.comparison.vs_allowable.ratio) }),
        el('td', { class: cmpClass(t.comparison.vs_scope_benchmark.status), text: times(t.comparison.vs_scope_benchmark.ratio) }),
        el('td', { class: 'decision-cell', 'data-tid': t.term_id }),
      ]));
    }
    renderDecisionColumns();
  }
  function renderDecisionColumns() {
    document.querySelectorAll('[data-decision-for]').forEach((cell) => {
      const fb = state.feedback.terms[cell.getAttribute('data-decision-for')];
      clear(cell).append(fb && fb.final_decision ? el('span', { class: 'pill human', text: DECISION_LABELS[fb.final_decision] + ' · human · not executed' }) : el('span', { class: 'pill na', text: 'no decision' }));
    });
    document.querySelectorAll('td.decision-cell').forEach((cell) => {
      const fb = state.feedback.terms[cell.getAttribute('data-tid')];
      clear(cell).append(fb && fb.final_decision ? el('span', { class: 'pill human', text: DECISION_LABELS[fb.final_decision] }) : el('span', { class: 'pill na', text: '—' }));
    });
  }
  function selectTerm(tid) {
    state.selected = tid;
    document.querySelectorAll('#term-table tbody tr').forEach((r) => r.classList.toggle('selected', r.getAttribute('data-tid') === tid));
    renderDetail();
  }
  function renderDetail() {
    const box = clear($('#detail'));
    const t = state.a.terms.find((x) => x.term_id === state.selected);
    if (!t) { box.appendChild(el('p', { text: 'Select a search term to see its evidence, hypotheses and recommendations, and to add your notes.' })); return; }
    const m = t.metrics, c = t.comparison, p = posture();
    const num = (label, value, cls) => el('div', { class: cls || '' }, [el('span', { text: label }), el('strong', { text: value })]);
    box.append(
      el('div', { class: 'detail-top' }, [
        el('div', {}, [el('span', { class: 'pill', text: t.match_type_source + ' match' }), el('span', { class: 'pill na', text: t.term_id })]),
        el('button', { type: 'button', class: 'add-input-btn', 'aria-describedby': 'add-input-hint', onclick: jumpToOperatorInput }, ['Add my input']),
      ]),
      el('span', { id: 'add-input-hint', class: 'sr-only', text: 'Jumps to the Your input section for this term and focuses the My insight field.' }),
      el('h2', { text: t.search_term }),
      el('div', { class: 'detail-numbers' }, [
        num('Clicks', count(m.clicks)), num('Cost', money(m.cost, 0)), num('CPC', money(m.cpc)),
        num('Signups (Regs)', count(m.signup)), num('FFT', 'unavailable', 'unavailable'), num('Paid subs (Subs)', count(m.paid_sub)),
        num('Cost / signup', money(m.cost_per_signup)), num('Signup → sub', pct(m.paid_sub_per_signup)), num('Cost / sub', money(m.cost_per_sub_recomputed)),
      ]),
      el('h3', { text: 'Comparisons' }),
      el('ul', {}, [
        el('li', {}, [el('span', { class: 'pill ' + cmpClass(c.vs_allowable.status), text: c.vs_allowable.status }), ' vs $' + Number(c.vs_allowable.reference) + ' allowable: ' + times(c.vs_allowable.ratio)]),
        el('li', {}, [el('span', { class: 'pill ' + cmpClass(c.vs_scope_benchmark.status), text: c.vs_scope_benchmark.status }), ' vs ' + money(c.vs_scope_benchmark.reference) + ' scope benchmark: ' + times(c.vs_scope_benchmark.ratio) + ' (observed, not a target)']),
        el('li', { text: 'To reach $181 at current cost: ' + count(c.allowable_reach.subs_needed) + ' subs = ' + pct(c.allowable_reach.sub_rate_needed) + ' of signups. Arithmetic, not a forecast; not financial break-even.' }),
      ]),
      el('h3', {}, ['Evidence ', el('span', { class: 'pill fact', text: 'fact' })]),
      el('p', { class: 'detail-note', text: t.evidence.summary }),
      el('h3', {}, ['Intent ', el('span', { class: 'pill hyp', text: 'hypothesis · ' + t.intent_hypothesis.confidence + ' confidence' })]),
      el('p', { class: 'detail-note', text: t.intent_hypothesis.text }),
      el('h3', { text: 'Missing information → what it would change' }),
      el('ul', {}, t.missing_information.map((mi) => el('li', {}, [el('strong', { text: mi.item }), ' — ' + mi.changes_decision]))),
      el('h3', {}, ['Conditional recommendation ', el('span', { class: 'pill', text: 'model · conditional' })]),
      el('p', { class: 'detail-note', text: t.conditional_recommendation.lean }),
      el('p', { class: 'detail-note' }, [el('strong', { text: 'Changes the decision if: ' }), t.conditional_recommendation.changes_decision_if]),
      branchBox('scale', t.conditional_recommendation.branches.scale, p === 'scale'),
      branchBox('maintain efficiency', t.conditional_recommendation.branches.maintain_efficiency, p === 'maintain_efficiency'),
      p ? el('p', { class: 'small', text: 'Highlighted branch follows the posture selected in Business Insights.' }) : el('p', { class: 'small', text: 'No posture selected; both branches shown.' }),
      renderOperatorSection(t),
    );
  }
  function jumpToOperatorInput() {
    const section = $('#detail .operator');
    const field = $('#detail textarea[id^=insight-]');
    if (!section || !field) return;
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    field.focus({ preventScroll: true });
  }
  function branchBox(label, text, selected) {
    return el('div', { class: 'branch' + (selected ? ' selected-branch' : '') }, [el('div', { class: 'label', text: 'IF POSTURE = ' + label.toUpperCase() + (selected ? ' · SELECTED' : '') }), el('div', { text: text })]);
  }

  // ---------- operator section (per term) ----------
  function renderOperatorSection(t) {
    const fb = termFeedback(t.term_id);
    const wrap = el('div', { class: 'operator' });
    wrap.append(
      el('h3', {}, ['Your input ', el('span', { class: 'pill human', text: 'human · saved on this browser only' })]),
      el('p', { class: 'small', text: 'Kept separate from the model analysis above. Mark each note as a confirmed fact or an unverified assumption. A decision here is your call for the record; it is not executed anywhere.' }),
    );
    // a. missing-data notes
    wrap.appendChild(el('label', { text: 'a. Missing-data notes' }));
    const notesBox = el('div');
    const renderNotes = () => {
      clear(notesBox);
      if (!fb.missing_data_notes.length) notesBox.appendChild(el('p', { class: 'entry-list-empty', text: 'No notes yet.' }));
      fb.missing_data_notes.forEach((n, i) => notesBox.appendChild(el('div', { class: 'entry' }, [
        el('textarea', { 'aria-label': 'Missing-data note ' + (i + 1), value: n.text, oninput: (e) => { n.text = e.target.value; saveFeedback(); } }),
        el('div', { class: 'row' }, [statusSelect(n.status, 'Note ' + (i + 1) + ' status', (v) => { n.status = v; saveFeedback(); }), el('button', { type: 'button', class: 'secondary small-btn danger', onclick: () => { fb.missing_data_notes.splice(i, 1); saveFeedback(); renderNotes(); } }, ['Remove'])]),
      ])));
      notesBox.querySelectorAll('textarea').forEach((ta, i) => { ta.value = fb.missing_data_notes[i].text; });
    };
    renderNotes();
    wrap.append(notesBox, el('button', { type: 'button', class: 'secondary small-btn', onclick: () => { fb.missing_data_notes.push({ text: '', status: 'unverified_assumption' }); saveFeedback(); renderNotes(); } }, ['+ Add note']));
    // b. Q&A
    wrap.appendChild(el('label', { text: 'b. Product-team questions and answers' }));
    const qaBox = el('div');
    const renderQA = () => {
      clear(qaBox);
      if (!fb.product_questions_and_answers.length) qaBox.appendChild(el('p', { class: 'entry-list-empty', text: 'No questions yet. Suggested questions are listed in the model\'s missing-information items above.' }));
      fb.product_questions_and_answers.forEach((q, i) => qaBox.appendChild(el('div', { class: 'entry' }, [
        el('div', { class: 'row' }, ['To: ', el('select', { 'aria-label': 'Question ' + (i + 1) + ' recipient', onchange: (e) => { q.to = e.target.value; saveFeedback(); } }, QA_TO.map((o) => el('option', { value: o, selected: o === q.to }, [o])))]),
        el('input', { type: 'text', placeholder: 'Question', 'aria-label': 'Question ' + (i + 1), value: q.question, oninput: (e) => { q.question = e.target.value; saveFeedback(); } }),
        el('textarea', { placeholder: 'Answer (leave empty if not yet answered)', 'aria-label': 'Answer ' + (i + 1), oninput: (e) => { q.answer = e.target.value; saveFeedback(); } }),
        el('div', { class: 'row' }, ['Answer is: ', statusSelect(q.answer_status || 'unverified_assumption', 'Answer ' + (i + 1) + ' status', (v) => { q.answer_status = v; saveFeedback(); }), el('button', { type: 'button', class: 'secondary small-btn danger', onclick: () => { fb.product_questions_and_answers.splice(i, 1); saveFeedback(); renderQA(); } }, ['Remove'])]),
      ])));
      qaBox.querySelectorAll('textarea').forEach((ta, i) => { ta.value = fb.product_questions_and_answers[i].answer; });
    };
    renderQA();
    wrap.append(qaBox, el('button', { type: 'button', class: 'secondary small-btn', onclick: () => { fb.product_questions_and_answers.push({ to: 'product', question: '', answer: '', answer_status: 'unverified_assumption' }); saveFeedback(); renderQA(); } }, ['+ Add question']));
    // c. insight
    const insightId = 'insight-' + t.term_id;
    wrap.appendChild(el('label', { for: insightId, text: 'c. My insight' }));
    const insightTa = el('textarea', { id: insightId, oninput: (e) => { fb.operator_insight.text = e.target.value; saveFeedback(); } });
    insightTa.value = fb.operator_insight.text;
    wrap.append(insightTa, el('div', { class: 'row', style: 'margin-top:6px' }, ['This insight is: ', statusSelect(fb.operator_insight.status, 'Insight status', (v) => { fb.operator_insight.status = v; saveFeedback(); })]));
    // d. decision
    const decId = 'decision-' + t.term_id;
    wrap.appendChild(el('label', { for: decId, text: 'd. Final decision (human decision · not executed)' }));
    wrap.appendChild(el('select', { id: decId, onchange: (e) => { fb.final_decision = e.target.value; saveFeedback(true); } }, DECISIONS.map((d) => el('option', { value: d, selected: d === (fb.final_decision || '') }, [DECISION_LABELS[d]]))));
    // e. rationale
    const ratId = 'rationale-' + t.term_id;
    wrap.appendChild(el('label', { for: ratId, text: 'e. Decision rationale' }));
    const ratTa = el('textarea', { id: ratId, oninput: (e) => { fb.decision_rationale = e.target.value; saveFeedback(); } });
    ratTa.value = fb.decision_rationale;
    wrap.append(ratTa, el('div', { class: 'human-note', text: 'Recorded as your decision and rationale. The model\'s conditional recommendation above is unchanged, and no advertising-account change is made or simulated.' }));
    return wrap;
  }
  function statusSelect(value, label, onChange) {
    return el('select', { 'aria-label': label, onchange: (e) => onChange(e.target.value) }, FACT_STATUS.map(([v, l]) => el('option', { value: v, selected: v === value }, [l])));
  }

  // ---------- view: Action Plan ----------
  function decisionCell(tid) { return el('td', { class: 'left', 'data-decision-for': tid }); }
  function list(items) { return el('ul', { style: 'margin:0;padding-left:16px' }, items.map((x) => el('li', { style: 'margin:3px 0', text: x }))); }
  function renderPlan() {
    const a = state.a;
    const neg = clear($('#negatives-table tbody'));
    for (const c of a.negative_candidates) neg.appendChild(el('tr', {}, [
      el('td', {}, [el('strong', { text: c.search_term })]), el('td', { class: 'left', text: '"' + c.proposed_negative + '"' }), el('td', { class: 'left', text: c.match_type_proposed + ' (proposed)' }),
      el('td', { class: 'left' }, [el('span', { class: 'pill hyp', text: c.status.replace('_', ' ') })]),
      el('td', { class: 'wrap' }, [list(c.confirmation_required)]), el('td', { class: 'wrap', text: c.becomes_actionable_if }), el('td', { class: 'wrap', text: c.does_not_apply_if }), decisionCell(c.term_id),
    ]));
    const add = clear($('#additions-table tbody'));
    for (const c of a.addition_isolation_candidates) add.appendChild(el('tr', {}, [
      el('td', {}, [el('strong', { text: c.search_term }), el('small', { text: c.status.replace('_', ' ') })]), el('td', { class: 'wrap', text: c.action }), el('td', { class: 'wrap' }, [list(c.precheck)]), el('td', { class: 'wrap', text: c.note || '' }), decisionCell(c.term_id),
    ]));
    const lp = clear($('#lp-table tbody'));
    for (const c of a.landing_page_tests) lp.appendChild(el('tr', {}, [el('td', {}, [el('strong', { text: c.search_term })]), el('td', { class: 'wrap', text: c.test }), el('td', { class: 'wrap' }, [list(c.precheck)]), el('td', { class: 'left' }, [el('span', { class: 'pill', text: c.status })])]));
    clear($('#least-certain')).append(el('p', { class: 'eyebrow', text: 'LEAST CERTAIN' }), el('h2', { text: 'Two candidates; the operator picks' }), el('p', { text: a.least_certain.text }), el('ul', {}, a.least_certain.candidates.map((c) => el('li', {}, [el('strong', { text: c.term }), ' — ' + c.why]))));
    const b = a.bidding_signal;
    clear($('#bidding-signal')).append(el('p', { class: 'eyebrow', text: 'BIDDING SIGNAL · CONCERN TO INVESTIGATE' }), el('h2', { text: b.decision }), el('p', { text: b.lean }), el('p', {}, [el('strong', { text: 'What would settle it: ' }), b.flips_if]));
    clear($('#justified-now')).append(el('p', { class: 'eyebrow', text: 'JUSTIFIED NOW ON THE SUPPLIED DATA' }), el('h2', { text: 'Investigations, not account changes' }), el('ul', {}, a.actions.justified_now.map((x) => el('li', {}, [el('strong', { text: x.action }), ' — ' + x.why]))));
    clear($('#requires-evidence')).append(el('p', { class: 'eyebrow', text: 'REQUIRES MORE EVIDENCE' }), el('h2', { text: 'Not decidable from the data alone' }), el('ul', {}, a.actions.requires_evidence.map((x) => el('li', {}, [el('strong', { text: x.action }), ' — needs: ' + x.needs + '. ' + x.why]))));
    renderDecisionColumns();
  }

  // ---------- view: Data & Run Log ----------
  function kv(pairs) { return el('dl', { class: 'kv' }, pairs.flatMap(([k, v, cls]) => [el('dt', { text: k }), el('dd', { class: cls || '', text: v })])); }
  function renderLog() {
    const a = state.a, cs = a.metrics.checks_summary;
    clear($('#checks-card')).append(el('p', { class: 'eyebrow', text: 'VERIFIED DATA CHECKS (STEP 1)' }), el('h2', { text: cs.overall === 'pass' ? 'All reconciliation checks passed' : 'Checks did not pass' }),
      kv([['Passes', String(cs.pass_count)], ['Failures', String(cs.fail_count)], ['Warnings', String(cs.warning_count)], ['Blocked decision checks', String(cs.blocked_count) + ' (operator thresholds unset, not invented)'], ['Missing-data items', String(cs.missing_count)]]),
      el('p', { class: 'small', text: 'Sample totals reconcile to $337,470 / 1,843 subs; channel sums (excluding Paid total) to $1,623,000 / 11,982. Cost/sub recomputed within a half-cent tolerance for every search term and real channel.' }));
    const v = a.versions, s = a.sources;
    clear($('#versions-card')).append(el('p', { class: 'eyebrow', text: 'SOURCE AND VERSION REFERENCES' }), el('h2', { text: 'What this dashboard is showing' }),
      kv([['Artifact', a.artifact + ' · schema ' + a.schema_version], ['Analysis basis', v.review_basis], ['Supersedes', v.review_supersedes.join(' · ')], ['Step 1 implementation', v.step1_implementation], ['Diagnosis v1', v.diagnosis_v1], ['Operator interview answers', s.operator_interview_answers],
        ['search_terms.csv', s.step1.inputs.search_terms.sha256, 'hash'], ['channel_summary.csv', s.step1.inputs.channel_summary.sha256, 'hash'], ['context', s.step1.inputs.context.sha256, 'hash'], ['review authoring', s.review.authoring_sha256, 'hash'], ['compute_metrics.py', s.step1.implementation_sha256, 'hash']]),
      el('h4', { text: 'Corrections applied in the analysis basis' }), el('ul', {}, v.corrections_applied.map((x) => el('li', { text: x }))));
    clear($('#missing-card')).append(el('p', { class: 'eyebrow', text: 'MISSING-DATA REGISTER → DECISION LIMIT' }), el('h2', { text: 'Unknown is not zero' }),
      el('div', { class: 'table-wrap' }, [el('table', {}, [el('thead', {}, [el('tr', {}, [el('th', { class: 'left', text: 'Item' }), el('th', { class: 'left', text: 'Status' }), el('th', { class: 'left', text: 'Limits' })])]),
        el('tbody', {}, a.metrics.missing_data_register.map((m) => el('tr', {}, [el('td', { text: m.item }), el('td', { class: 'left' }, [el('span', { class: 'pill na', text: m.status })]), el('td', { class: 'wrap', text: m.limits })])))])]));
    clear($('#warnings-card')).append(el('p', { class: 'eyebrow', text: 'WARNINGS (SUPPLIED VALUES PRESERVED)' }), el('h2', { text: a.metrics.warnings.length + ' warning(s) from step 1' }),
      el('ul', {}, a.metrics.warnings.map((w) => el('li', {}, [el('strong', { text: (w.channel || w.search_term || w.scope) + ': ' }), w.message + (w.supplied ? ' Supplied ' + w.supplied + ', recomputed ' + w.recomputed + '.' : '')]))));
    renderStorageCard();
  }
  function renderStorageCard() {
    const n = Object.values(state.feedback.terms).filter((t) => t.missing_data_notes.length || t.product_questions_and_answers.length || t.operator_insight.text || t.final_decision || t.decision_rationale).length;
    clear($('#storage-card')).append(el('p', { class: 'eyebrow', text: 'OPERATOR FEEDBACK STORAGE' }), el('h2', { text: 'Saved on this browser only' }),
      kv([['Storage key', state.storageKey, 'hash'], ['Terms with input', String(n)], ['Posture selection', postureLabel(posture())], ['Canonical baseline', 'unchanged; its validator requires empty operator fields, so feedback lives in localStorage and in exported operator_feedback.json']]),
      el('div', { class: 'row', style: 'margin-top:12px;display:flex;gap:10px;flex-wrap:wrap' }, [el('button', { type: 'button', class: 'secondary', onclick: exportFeedback }, ['Export feedback for Claude Code']), el('button', { type: 'button', class: 'secondary danger', onclick: clearFeedback }, ['Clear notes on this browser'])]));
  }
  function clearFeedback() {
    if (!window.confirm('Delete all operator notes saved on this browser for this analysis? Export first if you want to keep them.')) return;
    state.feedback = emptyFeedback(); saveFeedback(true); applyPostureToControls(); renderAll();
  }

  // ---------- tabs ----------
  const TABS = ['insights', 'terms', 'plan', 'log'];
  function showTab(name) {
    if (!TABS.includes(name)) name = 'insights';
    document.querySelectorAll('nav button').forEach((b) => b.classList.toggle('active', b.getAttribute('data-tab') === name));
    document.querySelectorAll('.view').forEach((v) => { v.hidden = v.id !== name; });
    if (location.hash !== '#' + name) history.replaceState(null, '', '#' + name);
  }
  function renderAll() {
    renderLevels(); renderChannels(); renderPatterns(); renderPostureNote(); renderBranchTable();
    renderTermTable(); renderDetail(); renderPlan(); renderLog();
  }

  // ---------- init ----------
  async function init() {
    document.querySelectorAll('nav button').forEach((b) => b.addEventListener('click', () => showTab(b.getAttribute('data-tab'))));
    $('#export-feedback').addEventListener('click', exportFeedback);
    $('#import-feedback').addEventListener('change', (e) => { const f = e.target.files && e.target.files[0]; if (f) importFeedbackFile(f); e.target.value = ''; });
    document.querySelectorAll('input[name=posture]').forEach((r) => r.addEventListener('change', onPostureChange));
    let a;
    try {
      const res = await fetch(ANALYSIS_URL, { cache: 'no-store' });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      a = await res.json();
      if (a.artifact !== 'search_ops_analysis' || !Array.isArray(a.terms)) throw new Error('unexpected artifact shape');
    } catch (e) {
      const box = $('#load-error'); box.hidden = false;
      box.textContent = 'Could not load ' + ANALYSIS_URL + ' (' + e.message + '). Serve the project root (see ui/README.md) and rebuild the canonical artifact with python3 src/build_canonical.py if it is missing.';
      return;
    }
    state.a = a;
    state.identity = identityOf(a);
    state.storageKey = 'searchops.feedback.' + state.identity.review_basis + '.' + state.identity.step1_search_terms_sha256.slice(0, 12) + '.' + state.identity.review_authoring_sha256.slice(0, 12);
    state.feedback = loadFeedback();
    $('#version-badge').textContent = a.versions.review_basis + ' · schema ' + a.schema_version + ' · ' + a.data_status.replace(/_/g, ' ');
    applyPostureToControls();
    renderAll();
    showTab(location.hash.replace('#', ''));
    window.addEventListener('hashchange', () => showTab(location.hash.replace('#', '')));
    if (location.hash === '#terms' && !state.selected) selectTerm(a.terms[0].term_id);
    setSaveStatus(hasAnyFeedback(state.feedback) ? 'Notes restored from this browser.' : 'Notes are saved on this browser only.');
    if (new URLSearchParams(location.search).get('selftest') === '1') {
      // Development self-test only: exposes internals for ui/selftest.js. Not used in normal operation.
      window.__searchops = { state, validateFeedback, loadFeedback, applyValidatedFeedback, exportPayload, selectTerm, DECISION_LABELS };
      document.body.appendChild(el('script', { src: 'selftest.js' }));
    }
  }
  document.addEventListener('DOMContentLoaded', init);
})();

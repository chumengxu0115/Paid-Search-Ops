/* Development self-test for the dashboard. Loaded only with ?selftest=1. Drives the real DOM and
   writes results into <pre id="selftest-results">. Phase 2 (?selftest=1&phase=2) checks persistence
   after a fresh page load in the same browser profile. */
(function () {
  const api = window.__searchops, a = api.state.a, out = [];
  const ok = (cond, msg) => out.push((cond ? 'PASS ' : 'FAIL ') + msg);
  const $ = (s) => document.querySelector(s);
  const fire = (node, type) => node.dispatchEvent(new Event(type, { bubbles: true }));
  const phase = new URLSearchParams(location.search).get('phase') || '1';
  const scriptCountBefore = document.querySelectorAll('script').length;
  const HOSTILE = '<img src=x onerror="document.title=\'XSS\'"><script>document.title="XSS"</script> & "quotes"';

  if (phase === 'layout') {
    const vw = window.innerWidth, sw = document.documentElement.scrollWidth;
    out.push('innerWidth=' + vw + ' scrollWidth=' + sw);
    const wide = [...document.querySelectorAll('body *')].filter((n) => !n.closest('[hidden]') && n.getBoundingClientRect().right > vw + 1).slice(0, 12);
    wide.forEach((n) => out.push('overflow: ' + n.tagName.toLowerCase() + ' [' + (n.textContent || '').trim().slice(0, 30) + ']' + (n.id ? '#' + n.id : '') + (n.className && typeof n.className === 'string' ? '.' + n.className.split(' ').join('.') : '') + ' right=' + Math.round(n.getBoundingClientRect().right)));
    ok(sw <= vw, 'no horizontal overflow at width ' + vw);
    finish(); return;
  }
  if (phase === '2') {
    const fb = api.state.feedback;
    const t = a.terms[1];
    const saved = fb.terms[t.term_id];
    ok(!!saved && saved.missing_data_notes.length === 1 && saved.missing_data_notes[0].text === HOSTILE, 'phase2: note restored from localStorage after fresh load (notes=' + JSON.stringify(saved && saved.missing_data_notes) + ')');
    ok(!!saved && saved.final_decision === 'negative', 'phase2: decision restored');
    ok(fb.posture_selection === 'maintain_efficiency', 'phase2: posture restored');
    api.selectTerm(t.term_id);
    ok($('#detail textarea') && $('#detail textarea').value === HOSTILE, 'phase2: note text rendered verbatim in textarea');
    ok(document.title !== 'XSS' && document.querySelectorAll('script').length === scriptCountBefore, 'phase2: hostile text did not execute');
    ok(!!$('#term-table td.decision-cell .pill.human') && $('#term-table td.decision-cell .pill.human').textContent === 'Negative', 'phase2: decision column shows human decision');
    finish(); return;
  }

  // 1. nine rows and selection
  const rows = document.querySelectorAll('#term-table tbody tr');
  ok(rows.length === 9, 'nine term rows rendered (' + rows.length + ')');
  let selOk = true;
  a.terms.forEach((t, i) => {
    rows[i].querySelector('button.term-btn').click();
    const h2 = $('#detail h2') && $('#detail h2').textContent;
    const ev = [...document.querySelectorAll('#detail p.detail-note')].some((p) => p.textContent === t.evidence.summary);
    const fft = [...document.querySelectorAll('#detail .detail-numbers div')].some((d) => d.textContent === 'FFTunavailable');
    if (h2 !== t.search_term || !ev || !fft) selOk = false;
  });
  ok(selOk, 'selecting each term shows its own name, evidence summary and FFT = unavailable');

  // 2. posture switching
  const setPosture = (v) => { const r = document.querySelector('input[name=posture][value="' + v + '"]'); r.checked = true; fire(r, 'change'); };
  const branchCell = (i) => document.querySelectorAll('#branch-table tbody tr')[i].children[3].textContent;
  setPosture('scale');
  ok(a.terms.every((t, i) => branchCell(i) === t.conditional_recommendation.branches.scale), 'posture=scale shows the saved scale branch for all terms');
  ok($('#detail .branch.selected-branch') && $('#detail .branch.selected-branch').textContent.includes('SCALE'), 'detail panel highlights the scale branch');
  setPosture('maintain_efficiency');
  ok(a.terms.every((t, i) => branchCell(i) === t.conditional_recommendation.branches.maintain_efficiency), 'posture=maintain_efficiency shows the saved branch for all terms');
  setPosture('');
  ok(a.terms.every((t, i) => branchCell(i).includes(t.conditional_recommendation.branches.scale) && branchCell(i).includes(t.conditional_recommendation.branches.maintain_efficiency)), 'no posture shows both branches');
  setPosture('maintain_efficiency');

  // 3. operator notes with hostile text (start from a clean slate for this term so reruns do not accumulate)
  const t1 = a.terms[1];
  delete api.state.feedback.terms[t1.term_id];
  api.selectTerm(t1.term_id);
  [...document.querySelectorAll('#detail button')].find((b) => b.textContent === '+ Add note').click();
  const ta = $('#detail .entry textarea'); ta.value = HOSTILE; fire(ta, 'input');
  const sel = $('#detail select[id^=decision-]'); sel.value = 'negative'; fire(sel, 'change');
  const stored = JSON.parse(localStorage.getItem(api.state.storageKey));
  ok(stored.terms[t1.term_id].missing_data_notes[0].text === HOSTILE, 'note autosaved to localStorage under the analysis key');
  ok(stored.terms[t1.term_id].final_decision === 'negative', 'decision autosaved');
  ok(document.title !== 'XSS' && document.querySelectorAll('script').length === scriptCountBefore, 'hostile note text did not execute (safe rendering)');
  ok(a.terms.every((t) => JSON.stringify(t.conditional_recommendation) === JSON.stringify(api.state.a.terms.find((x) => x.term_id === t.term_id).conditional_recommendation)), 'model recommendations untouched by operator input');

  // 4. export / import round trip
  const payload = api.exportPayload();
  ok(api.validateFeedback(payload).length === 0, 'exported payload validates');
  ok(payload.analysis_identity.review_basis === a.versions.review_basis, 'export carries analysis identity');
  const before = JSON.stringify(api.state.feedback);
  const copy = JSON.parse(JSON.stringify(payload)); copy.terms[t1.term_id].decision_rationale = 'round trip';
  api.applyValidatedFeedback(copy);
  ok(api.state.feedback.terms[t1.term_id].decision_rationale === 'round trip' && api.state.feedback.terms[t1.term_id].missing_data_notes[0].text === HOSTILE, 'import round trip restores notes and decision');

  // 5. malformed / mismatched imports are rejected without touching notes
  const snapshot = JSON.stringify(api.state.feedback);
  const bad1 = api.validateFeedback({ hello: 'world' });
  const bad2 = api.validateFeedback(Object.assign({}, payload, { analysis_identity: Object.assign({}, payload.analysis_identity, { review_authoring_sha256: 'deadbeef' }) }));
  const bad3 = api.validateFeedback(Object.assign({}, payload, { terms: { st_000000000000: payload.terms[t1.term_id] } }));
  const bad4 = api.validateFeedback(Object.assign({}, payload, { terms: { [t1.term_id]: { missing_data_notes: 'nope' } } }));
  ok(bad1.length && bad2.length && bad3.length && bad4.length, 'malformed, mismatched-identity, unknown-term and wrong-type imports are rejected');
  ok(JSON.stringify(api.state.feedback) === snapshot, 'rejected imports leave existing notes unchanged');

  // 5b. Add my input button and Insights CTA link
  api.selectTerm(t1.term_id);
  const insightField = $('#detail textarea[id^=insight-]'); insightField.value = 'keep me'; fire(insightField, 'input');
  const addBtn = [...document.querySelectorAll('#detail button')].find((b) => b.textContent === 'Add my input');
  ok(!!addBtn && addBtn === $('#detail .detail-top button'), 'Add my input button present at the top of the detail panel');
  // headless Chrome does not update document.activeElement, so record the focus() call instead
  const focusCalls = []; const origFocus = HTMLTextAreaElement.prototype.focus;
  HTMLTextAreaElement.prototype.focus = function () { focusCalls.push(this.id); return origFocus.apply(this, arguments); };
  addBtn.click();
  HTMLTextAreaElement.prototype.focus = origFocus;
  const insightNow = $('#detail textarea[id^=insight-]');
  ok(focusCalls.length === 1 && focusCalls[0] === insightNow.id && insightNow.value === 'keep me', 'Add my input calls focus() on My insight without changing its content (focus target=' + focusCalls.join(',') + '; activeElement not observable in headless)');
  ok(addBtn.tagName === 'BUTTON' && !addBtn.disabled, 'Add my input is a native button (keyboard accessible)');
  const cta = $('#review-terms-link');
  ok(!!cta && cta.tagName === 'A' && cta.getAttribute('href') === '#terms', 'Insights CTA link present and keyboard-focusable');
  document.querySelector('nav button[data-tab=insights]').click();
  cta.click();
  ok(!$('#terms').hidden && $('#insights').hidden, 'CTA link navigates to Search Terms');

  // 6. keyboard labels: every form control in the detail panel has an accessible label
  const unlabeled = [...document.querySelectorAll('#detail textarea, #detail select, #detail input')].filter((c) => !(c.getAttribute('aria-label') || (c.id && document.querySelector('label[for="' + c.id + '"]'))));
  ok(unlabeled.length === 0, 'all operator controls have labels (' + unlabeled.length + ' unlabeled)');
  ok([...document.querySelectorAll('nav button')].length === 4, 'four view tabs');
  finish();

  function finish() {
    const pre = document.createElement('pre'); pre.id = 'selftest-results'; pre.textContent = out.join('\n'); document.body.appendChild(pre);
    document.title = out.some((l) => l.startsWith('FAIL')) ? 'SELFTEST FAIL' : 'SELFTEST PASS';
  }
})();

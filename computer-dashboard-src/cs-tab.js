/* ======================================================================
   CS.  COMPUTER  —  chapter-wise practice sets from the Sunrise Classes
   Computer MCQ book (465 pages, 11 chapters).
   Injected by computer-dashboard-src/integrate.py; edit it there, not here.
   The bank lives in window.csData / window.csMeta and is kept apart from
   the authentic PYQs: it never enters a year, sectional, topic, subtopic
   or custom PYQ mock, and the PYQ data audit ignores it.
   ====================================================================== */
var CS = { ch: 0, view: 'sets', bset: 1, pick: {}, open: {} };
var CS_BY_SET = {};
var CS_BY_CH = {};
CDATA.forEach(function (q) {
  var k = q.csChapter + '-' + q.csSet;
  (CS_BY_SET[k] = CS_BY_SET[k] || []).push(q);
  (CS_BY_CH[q.csChapter] = CS_BY_CH[q.csChapter] || []).push(q);
});

/* progress kept in its own key so the PYQ store's 60-attempt history cap
   never erases which sets have been covered */
var CsStore = (function () {
  var KEY = 'upsc.iss.cs.v1';
  var cache = null;
  function blank() { return { v: 1, sets: {}, q: {} }; }
  function load() {
    if (cache) return cache;
    try {
      var raw = window.localStorage.getItem(KEY);
      cache = raw ? JSON.parse(raw) : blank();
    } catch (e) { cache = blank(); }
    if (!cache || cache.v !== 1 || !cache.sets || !cache.q) cache = blank();
    return cache;
  }
  function save() {
    try { window.localStorage.setItem(KEY, JSON.stringify(load())); } catch (e) {}
  }
  function replace(obj) {
    cache = (obj && obj.v === 1 && obj.sets && obj.q) ? obj : blank();
    save();
  }
  return { d: load, save: save, replace: replace, reset: function () { cache = blank(); save(); } };
})();

/* text renderer for this bank: `code spans` are shown literally (so C
   operators such as *, $, | and <> can never be read as markup), the rest
   goes through the shared markdown-lite + KaTeX renderer */
function csR(s) {
  if (s === null || s === undefined || s === '') return '';
  var parts = String(s).split('`'), h = '';
  for (var i = 0; i < parts.length; i++) {
    h += (i % 2) ? '<code>' + E(parts[i]) + '</code>' : R(parts[i]);
  }
  return h;
}

function csBody(q) {
  var h = csR(q.question);
  if (q.code) h += '<pre class="cs-code">' + E(q.code) + '</pre>';
  if (q.stmts && q.stmts.length) {
    h += '<ol class="stmts">';
    q.stmts.forEach(function (s) { h += '<li>' + csR(s) + '</li>'; });
    h += '</ol>';
  }
  if (q.ask) h += '<div class="ask">' + csR(q.ask) + '</div>';
  return h;
}

function csChapter(num) {
  var out = null;
  (CMETA ? CMETA.chapters : []).forEach(function (c) { if (c.num === +num) out = c; });
  return out;
}

function csSheet(num) {
  var out = null;
  (CMETA ? CMETA.sheets : []).forEach(function (s) { if (s.ch === +num) out = s; });
  return out;
}

function csSetQs(ch, k) { return CS_BY_SET[ch + '-' + k] || []; }
function csSetName(ch, k) { return 'Computer · Ch ' + ch + ' · Set ' + k; }

function csRelatedPyqs(c) {
  return DATA.filter(function (q) { return c.relCodes.indexOf(q.topicCode) >= 0; });
}

function csSourceLine(q) {
  var c = csChapter(q.csChapter);
  if (q.isBooster) {
    return 'ISS Booster question, written for this dashboard (not in the book) to complete Chapter ' +
      q.csChapter + (c ? ' (' + E(c.title) + ')' : '') + ' Set ' + q.csSet +
      (q.pyqRef ? ' &middot; modelled on ' + E(q.pyqRef) : '');
  }
  return 'Sunrise Classes, <i>Computer MCQ &mdash; Chapter-wise Practice Set</i>, Chapter ' + q.csChapter +
    (c ? ' (' + E(c.title) + ')' : '') + ', Q' + q.csNum + ' &middot; question on PDF p. ' + q.qPage +
    (q.aPage ? ', explanation on PDF p. ' + q.aPage : '') + ' &middot; Set ' + q.csSet;
}

/* coverage helpers */
function csCov(qs) {
  var st = CsStore.d().q, seen = 0, ok = 0;
  qs.forEach(function (q) {
    if (st.hasOwnProperty(q.id)) { seen++; if (st[q.id] === 1) ok++; }
  });
  return { n: qs.length, seen: seen, ok: ok };
}

function csMarkQ(qid, correct) {
  var d = CsStore.d();
  d.q[qid] = correct ? 1 : 0;
  CsStore.save();
}

/* called from persistAttempt() for every submitted Computer session */
function csRecord(sess) {
  var d = CsStore.d(), r = sess.result;
  r.perQ.forEach(function (p) {
    if (p.status === 'correct') d.q[p.qid] = 1;
    else if (p.status === 'incorrect') d.q[p.qid] = 0;
  });
  if (sess.csSetId) {
    var s = d.sets[sess.csSetId] || { att: 0, best: 0, bestExam: null, last: 0, ts: 0 };
    var score = r.total ? Math.round(100 * r.correct / r.total) : 0;
    s.att++; s.last = score; s.ts = sess.endTs || Date.now();
    if (score > s.best) s.best = score;
    if (sess.mode === 'exam') s.bestExam = Math.max(s.bestExam === null ? 0 : s.bestExam, Math.round(r.pct));
    d.sets[sess.csSetId] = s;
  }
  CsStore.save();
}

/* reveal order for the Computer bank:
   verdict -> Explanation -> Exam Shortcut -> (answer-key note) -> source */
function csRevealPanes(q, chosen, opts) {
  opts = opts || {};
  if (ROUTE.name === 'study') opts.peek = true;
  var h = '';
  var answered = chosen !== null && chosen !== undefined;
  var ok = answered && chosen === q.correctAnswer;
  var cls = !answered ? (opts.peek ? 'verdict-ok' : 'verdict-skip') : (ok ? 'verdict-ok' : 'verdict-bad');
  var verdict = !answered ? (opts.peek ? 'Answer' : 'Not answered') : (ok ? 'Correct' : 'Incorrect');
  h += '<div class="pane ' + cls + '"><div class="hd"><span class="step">1</span>' + E(verdict) +
    '</div><div class="bd">';
  if (!opts.peek) {
    h += '<div class="small"><b>Your answer:</b> ' +
      (answered ? '(' + LET[chosen] + ') ' + csR(q.options[chosen])
                : '<span class="muted">not attempted</span>') + '</div>';
  }
  h += '<div class="small' + (opts.peek ? '' : ' mt') + '"><b>Correct answer:</b> (' +
    LET[q.correctAnswer] + ') ' + csR(q.options[q.correctAnswer]) + '</div>';
  h += '</div></div>';

  h += '<div class="pane cs-exp"><div class="hd"><span class="step">2</span>Explanation</div>' +
    '<div class="bd">' + csR(q.explanation) + '</div></div>';

  h += '<div class="pane cs-short"><div class="hd"><span class="step">3</span>Exam Shortcut ' +
    '<span class="chip">~15 sec</span></div><div class="bd">' + csR(q.examShortcut) + '</div></div>';

  if (q.keyNote) {
    h += '<div class="pane cs-keyfix"><div class="hd">Answer-key note</div><div class="bd small">' +
      csR(q.keyNote) + '</div></div>';
  }
  if (opts.topic !== false) {
    h += '<div class="pane"><div class="hd">Source &amp; syllabus</div><div class="bd small">' +
      '<p>' + csSourceLine(q) + '</p><p><b>Syllabus.</b> ' + E(q.unit) + ' › ' + E(q.topicCode) + ' ' +
      E(q.topic) + '</p></div></div>';
  }
  return h;
}

function csOptionList(q, pick) {
  var done = pick !== undefined && pick !== null;
  var h = '<ul class="opts">';
  for (var i = 0; i < q.options.length; i++) {
    var cls = 'opt';
    if (done) {
      if (i === q.correctAnswer) cls += ' correct';
      else if (i === pick) cls += ' wrong';
    }
    h += '<li><button type="button" class="' + cls + '"' + (done ? ' disabled' : '') +
      ' data-act="csOpt" data-qid="' + E(q.id) + '" data-i="' + i + '">' +
      '<span class="k">' + LET[i] + '</span><span class="v">' + csR(q.options[i]) + '</span></button></li>';
  }
  return h + '</ul>';
}

function csItem(q, n) {
  var pick = CS.pick.hasOwnProperty(q.id) ? CS.pick[q.id] : null;
  var open = pick !== null || !!CS.open[q.id];
  var h = '<li class="cs-item" id="cs-' + E(q.id.replace(/[^A-Za-z0-9-]/g, '-')) + '">' +
    '<div class="top"><span class="cs-n">' + E(q.csLabel) + '</span><span class="id">' + E(q.id) + '</span>' +
    '<span class="chip">' + E(q.questionType) + '</span>' +
    '<span class="chip">' + E(q.topicCode) + '</span>' +
    (q.isBooster ? '<span class="chip brand">ISS Booster</span>' : '<span class="chip">p. ' + q.qPage + '</span>') +
    (q.keyNote ? '<span class="chip warn" title="The printed answer key was corrected">key corrected</span>' : '') +
    '</div>' +
    '<div class="qtext">' + csBody(q) + '</div>' + csOptionList(q, pick) +
    '<div class="btnrow">' +
    (open ? '<button type="button" class="btn sm" data-act="csHide" data-qid="' + E(q.id) + '">' +
            (pick !== null ? 'Try again' : 'Hide explanation') + '</button>'
          : '<button type="button" class="btn sm" data-act="csShow" data-qid="' + E(q.id) + '">Show explanation</button>') +
    bookmarkBtn(q.id) +
    '<button type="button" class="btn sm ghost" data-act="study" data-qid="' + E(q.id) +
    '" data-back="cs">Study card</button></div>';
  if (open) {
    h += '<div class="reveal">' + csRevealPanes(q, pick, { peek: pick === null, topic: false }) + '</div>';
  }
  return h + '</li>';
}

function csSetsView(c) {
  var sets = CsStore.d().sets;
  var next = null;
  c.sets.forEach(function (s) {
    if (next === null && !sets[c.num + '-' + s.k]) next = s.k;
  });
  var h = '';
  var cov = csCov(CS_BY_CH[c.num] || []);
  h += '<div class="card cs-next"><div class="grow"><h3 style="margin:0 0 4px">' +
    (next ? 'Next up: Set ' + next + ' of ' + c.sets.length
          : 'All ' + c.sets.length + ' sets attempted') + '</h3>' +
    '<div class="small muted">Work the sets in order until every question of the chapter is covered. ' +
    '<b>Learning</b> opens the explanation and then the exam shortcut after each answer; <b>Exam</b> is timed, ' +
    'uses the marking scheme in Settings and reveals everything in the review.</div>' +
    '<div class="cs-cov"><span>Covered ' + cov.seen + '/' + cov.n + '</span><div class="progbar"><i class="ok" style="width:' +
    fx(pct(cov.seen, cov.n), 1) + '%"></i></div><span>' + cov.ok + ' right on last try</span></div></div>' +
    (next ? '<div class="btnrow"><button type="button" class="btn primary" data-act="csStart" data-set="' + next +
      '" data-mode="learn">Start Set ' + next + ' · Learning</button>' +
      '<button type="button" class="btn" data-act="csStart" data-set="' + next + '" data-mode="exam">Exam</button></div>' : '') +
    '</div>';

  h += '<div class="cs-sets">';
  c.sets.forEach(function (s) {
    var qs = csSetQs(c.num, s.k);
    var rec = sets[c.num + '-' + s.k];
    var sc = csCov(qs);
    h += '<div class="cs-set' + (s.k === next ? ' next' : '') + '">' +
      '<div class="hd"><b>Set ' + s.k + '</b><span class="rng">Q ' + s.from + '–' + s.to + (s.boost ? ' + ' + s.boost + ' ISS Booster' + (s.boost > 1 ? 's' : '') : '') + ' · ' + s.n + ' questions</span></div>' +
      (s.themes ? '<div class="themes">' + E(s.themes) + '</div>' : '') +
      '<div class="progbar"><i class="' + (sc.seen === sc.n ? 'ok' : '') + '" style="width:' + fx(pct(sc.seen, sc.n), 1) + '%"></i></div>' +
      '<div class="stat"><span><b>' + sc.seen + '/' + sc.n + '</b> covered</span>' +
      (rec ? '<span>best <b>' + rec.best + '%</b></span><span>last <b>' + rec.last + '%</b></span><span>' + rec.att + ' attempt' + (rec.att > 1 ? 's' : '') + '</span>'
           : '<span>not attempted yet</span>') +
      (rec && rec.bestExam !== null ? '<span>exam <b>' + rec.bestExam + '%</b></span>' : '') + '</div>' +
      '<div class="btnrow"><button type="button" class="btn sm primary" data-act="csStart" data-set="' + s.k +
      '" data-mode="learn">Learning</button><button type="button" class="btn sm" data-act="csStart" data-set="' + s.k +
      '" data-mode="exam">Exam</button><button type="button" class="btn sm ghost" data-act="csBrowse" data-set="' + s.k +
      '">Read</button></div></div>';
  });
  h += '</div>';
  return h;
}

function csSheetView(c) {
  var sh = csSheet(c.num);
  var h = '<div class="card"><h2>Crisp pointers &mdash; Chapter ' + c.num + ' · ' + E(c.title) +
    ' <span class="cs-badge">ISS PAPER-I · OBJECTIVE</span></h2>' +
    '<p class="card-sub">Last-day revision bullets for the Computer Application section of UPSC ISS ' +
    'Statistics Paper-I: the facts, definitions, conversions and traps this chapter feeds into the objective paper.</p>' +
    '<div class="btnrow noprint"><button type="button" class="btn sm" data-act="csPrint">Print these pointers</button>' +
    '<button type="button" class="btn sm ghost" data-act="csView" data-v="sets">Back to the sets</button></div></div>';
  if (!sh) return h + '<div class="empty">No pointers for this chapter yet.</div>';
  h += '<div class="cs-sheets">';
  sh.sections.forEach(function (s, i) {
    h += '<div class="card cs-sheet' + (s.pyq ? ' pyq' : '') + '"><h3><span class="k">' +
      (s.pyq ? 'PYQ' : c.num + '.' + (i + 1)) + '</span>' + E(s.title) + '</h3><ul>';
    s.items.forEach(function (b) { h += '<li>' + csR(b) + '</li>'; });
    h += '</ul></div>';
  });
  h += '</div>';
  /* the ISS examiner's pattern for the syllabus topics this chapter feeds */
  var ti = META.topicIntel || {};
  var intel = c.relCodes.map(function (k) { return ti[k]; }).filter(Boolean);
  if (intel.length) {
    h += '<h3 class="mt">What ISS has actually asked from this chapter</h3><div class="cs-sheets">';
    intel.forEach(function (t) {
      h += '<div class="card cs-sheet pyq"><h3><span class="k">' + E(t.code) + '</span>' + E(t.name) + '</h3>' +
        '<p class="small"><b>Weight.</b> ' + E(t.weight) + '</p>' +
        '<p class="small"><b>Examiner’s pattern.</b> ' + R(t.pattern) + '</p>' +
        '<p class="small"><b>Must-know.</b> ' + R(t.mustKnow) + '</p></div>';
    });
    h += '</div>';
  }
  return h;
}

function csBrowseView(c) {
  var k = Math.min(Math.max(1, CS.bset), c.sets.length);
  CS.bset = k;
  var qs = csSetQs(c.num, k);
  var h = '<div class="card"><h2>Read &amp; self-test · Set ' + k + '</h2>' +
    '<p class="card-sub">Every question of the set in book order. Tap an option to check it, or open the ' +
    'explanation straight away.</p><div class="cs-subtabs">';
  c.sets.forEach(function (s) {
    h += '<button type="button" class="cs-sub' + (s.k === k ? ' on' : '') + '" data-act="csBrowse" data-set="' + s.k +
      '">Set ' + s.k + '<span class="n">' + s.n + '</span></button>';
  });
  h += '</div><div class="btnrow mt"><button type="button" class="btn sm primary" data-act="csStart" data-set="' + k +
    '" data-mode="learn">Practise Set ' + k + ' (Learning)</button><button type="button" class="btn sm" data-act="csStart" data-set="' + k +
    '" data-mode="exam">Exam</button></div></div>';
  h += '<ul class="list cs-list">';
  qs.forEach(function (q, i) { h += csItem(q, i + 1); });
  return h + '</ul>';
}

function csPyqView(c) {
  var rel = csRelatedPyqs(c);
  var h = '<div class="card"><h2>Related previous-year questions</h2>' +
    '<p class="card-sub">Authentic UPSC ISS Paper-I computer questions (2018–2026) from the syllabus topics ' +
    'this chapter covers. They open in the normal PYQ engine.</p><div class="cs-pyqrow">';
  var ti = META.topicIntel || {};
  c.relCodes.forEach(function (k) {
    var n = DATA.filter(function (q) { return q.topicCode === k; }).length;
    h += '<span class="chip">' + E(k) + ' ' + E(ti[k] ? ti[k].name : '') + ' · ' + n + '</span>';
  });
  h += '</div><div class="btnrow"><button type="button" class="btn primary" data-act="csPyq"' +
    (rel.length ? '' : ' disabled') + '>Practise all ' + rel.length + ' related PYQs</button></div></div>';
  if (rel.length) {
    h += '<ul class="list">';
    rel.slice().sort(function (a, b) { return b.year - a.year || a.questionNumber - b.questionNumber; })
      .forEach(function (q) {
        h += '<li><div class="top"><span class="pyq-badge">' + q.year + ' Q' + q.questionNumber + '</span>' +
          '<span class="id">' + E(q.topicCode) + '</span></div><div class="small">' + R(q.question) + '</div>' +
          '<div class="btnrow mt"><button type="button" class="btn sm ghost" data-act="study" data-qid="' + E(q.id) +
          '" data-back="cs">Study card</button></div></li>';
      });
    h += '</ul>';
  }
  return h;
}

V.cs = function () {
  var h = crumb(['Home', 'Computer']);
  if (!CMETA || !CDATA.length) {
    return h + '<div class="card"><h1>Computer bank not loaded</h1></div>';
  }
  var c = csChapter(CS.ch) || CMETA.chapters[0];
  CS.ch = c.num;
  var views = { sets: 'Practice sets', sheet: 'Crisp pointers', read: 'Read & self-test', pyq: 'Related PYQs' };
  if (!views[CS.view]) CS.view = 'sets';
  h = crumb(['Home', 'Computer', 'Chapter ' + c.num, views[CS.view]]);

  var all = csCov(CDATA);
  h += '<div class="card cs-head"><h1>Computer <span class="cs-badge">CHAPTER-WISE SETS · ISS PAPER-I</span></h1>' +
    '<p class="card-sub">Every question of ' + E(CMETA.source) + ' (' + CMETA.pages + ' pages), dealt chapter by ' +
    'chapter into sets of ' + CMETA.setMin + '–' + CMETA.setMax + '. Each answer opens with the verdict, then the ' +
    'explanation, then a 15-second exam shortcut. Every chapter also has a crisp-pointer sheet for the objective paper.</p>' +
    '<div class="kpis">' +
    '<div class="kpi"><div class="v">' + CMETA.total + '</div><div class="l">Questions</div></div>' +
    '<div class="kpi"><div class="v">' + CMETA.chapters.length + '</div><div class="l">Chapters</div></div>' +
    '<div class="kpi"><div class="v">' + CMETA.nSets + '</div><div class="l">Practice sets</div></div>' +
    '<div class="kpi ok"><div class="v">' + fx(pct(all.seen, all.n), 0) + '%</div><div class="l">Covered</div></div>' +
    '</div>' +
    '<details class="cs-prov"><summary>Book bank, not previous-year questions · about the source</summary>' +
    '<div class="banner info">' + E(CMETA.provenance) + '</div></details></div>';

  h += '<div class="cs-tabs" role="tablist" aria-label="Chapters">';
  CMETA.chapters.forEach(function (cc) {
    var on = cc.num === c.num;
    var cv = csCov(CS_BY_CH[cc.num] || []);
    h += '<button type="button" role="tab" aria-selected="' + on + '" class="cs-tab' + (on ? ' on' : '') +
      '" data-act="csCh" data-ch="' + cc.num + '"><b>Chapter ' + cc.num + '</b><span>' + E(cc.title) +
      '</span><small>' + cc.n + ' questions · ' + cc.sets.length + ' sets</small>' +
      '<div class="progbar"><i style="width:' + fx(pct(cv.seen, cv.n), 1) + '%"></i></div></button>';
  });
  h += '</div>';

  var rel = csRelatedPyqs(c);
  h += '<div class="card cs-chap"><div class="cs-chap-hd"><h2>Chapter ' + c.num + ' · ' + E(c.title) + '</h2>' +
    '<div class="btnrow">' +
    '<button type="button" class="btn sm" data-act="csChapterMock" data-mode="exam">Chapter mock (' + c.n + ')</button>' +
    '<button type="button" class="btn sm ghost" data-act="csChapterMock" data-mode="random">Random 20</button>' +
    '</div></div><div class="cs-subtabs" role="tablist" aria-label="Chapter views">';
  [['sets', 'Practice sets', c.sets.length], ['sheet', 'Crisp pointers · ISS Paper-I', null],
   ['read', 'Read & self-test', null], ['pyq', 'Related PYQs', rel.length]].forEach(function (v) {
    var on = CS.view === v[0];
    h += '<button type="button" role="tab" aria-selected="' + on + '" class="cs-sub' + (on ? ' on' : '') +
      '" data-act="csView" data-v="' + v[0] + '">' + E(v[1]) + (v[2] !== null ? '<span class="n">' + v[2] + '</span>' : '') +
      '</button>';
  });
  h += '</div></div>';

  if (CS.view === 'sheet') h += csSheetView(c);
  else if (CS.view === 'read') h += csBrowseView(c);
  else if (CS.view === 'pyq') h += csPyqView(c);
  else h += csSetsView(c);
  return h;
};

function csHomeSection() {
  if (!CMETA || !CDATA.length) return '';
  var h = '<h2 class="mt">Computer · chapter-wise sets <span class="cs-badge">BOOK BANK &middot; NOT PYQ</span></h2>';
  h += '<div class="grid g3">';
  CMETA.chapters.forEach(function (c) {
    var cv = csCov(CS_BY_CH[c.num] || []);
    h += tile('csGo', { ch: c.num }, 'Chapter ' + c.num + ' · ' + E(c.title),
      c.sets.length + ' sets of ' + CMETA.setMin + '–' + CMETA.setMax + ' · learning &amp; exam mode · crisp pointers',
      c.n + ' questions · ' + cv.seen + ' covered');
  });
  h += tile('csGo', { ch: CMETA.chapters[0].num, v: 'sheet' }, 'Crisp pointers for ISS Paper-I',
    'Chapter-wise bullet sheets for last-day revision of the Computer section.', CMETA.chapters.length + ' sheets');
  h += tile('csMix', { n: 20 }, 'Computer section drill (20)',
    'Twenty questions drawn across all chapters, timed like the Computer part of Paper-I.', 'Strict exam');
  h += '</div>';
  return h;
}

function csStartSet(k, mode) {
  var c = csChapter(CS.ch);
  if (!c) return;
  var qs = csSetQs(c.num, k);
  if (!qs.length) return;
  var st = Store.d().settings;
  var exam = mode === 'exam';
  buildSession({
    kind: 'cs',
    name: csSetName(c.num, k),
    desc: 'COMPUTER BOOK BANK (not PYQ) · Chapter ' + c.num + ' ' + c.title + ' · Q ' +
      c.sets[k - 1].from + '–' + c.sets[k - 1].to + (c.sets[k - 1].boost ? ' + ' + c.sets[k - 1].boost + ' boosters' : '') + ' · ' + qs.length + ' questions · mode: ' +
      (exam ? 'Strict Exam' : 'Learning'),
    mode: exam ? 'exam' : 'learn',
    questions: qs,
    shuffleQ: exam, shuffleO: false,
    timed: exam && st.timerOn,
    minutes: Math.round(qs.length * st.minutesPerQuestion),
    authentic: false
  });
  S.csSetId = c.num + '-' + k;
}

function csStartPool(qs, name, desc) {
  if (!qs.length) return;
  var st = Store.d().settings;
  buildSession({
    kind: 'cs', name: name, desc: desc, mode: 'exam', questions: qs,
    shuffleQ: true, shuffleO: false, timed: st.timerOn,
    minutes: Math.round(qs.length * st.minutesPerQuestion), authentic: false
  });
}

/* delegated clicks for this tab; returns true when handled */
function csClick(act, t) {
  var qid = t.getAttribute('data-qid');
  switch (act) {
    case 'csGo':
      CS.ch = +t.getAttribute('data-ch');
      CS.view = t.getAttribute('data-v') || 'sets';
      go('cs');
      return true;
    case 'csCh':
      CS.ch = +t.getAttribute('data-ch'); CS.bset = 1;
      render();
      return true;
    case 'csView': CS.view = t.getAttribute('data-v'); render(); window.scrollTo(0, 0); return true;
    case 'csBrowse':
      CS.view = 'read'; CS.bset = +t.getAttribute('data-set') || 1;
      render(); window.scrollTo(0, 0);
      return true;
    case 'csOpt': {
      var q = BY_ID[qid];
      var i = +t.getAttribute('data-i');
      CS.pick[qid] = i;
      if (q) csMarkQ(qid, i === q.correctAnswer);
      render();
      return true;
    }
    case 'csShow': CS.open[qid] = true; render(); return true;
    case 'csHide': delete CS.open[qid]; delete CS.pick[qid]; render(); return true;
    case 'csPrint': window.print(); return true;
    case 'csStart':
      if (S && !S.finished && ROUTE.name === 'exam') return true;
      csStartSet(+t.getAttribute('data-set'), t.getAttribute('data-mode'));
      return true;
    case 'csChapterMock': {
      var c = csChapter(CS.ch);
      if (!c) return true;
      var qs = (CS_BY_CH[c.num] || []).slice();
      if (t.getAttribute('data-mode') === 'random') {
        shuffle(qs);
        csStartPool(qs.slice(0, 20), 'Computer · Ch ' + c.num + ' · Random 20',
          'COMPUTER BOOK BANK (not PYQ) · 20 random questions from Chapter ' + c.num + ' · mode: Strict Exam');
      } else {
        csStartPool(qs, 'Computer · Ch ' + c.num + ' · Chapter mock',
          'COMPUTER BOOK BANK (not PYQ) · all ' + qs.length + ' questions of Chapter ' + c.num + ' · mode: Strict Exam');
      }
      return true;
    }
    case 'csMix': {
      var n = +t.getAttribute('data-n') || 20;
      var pool = CDATA.slice();
      shuffle(pool);
      csStartPool(pool.slice(0, n), 'Computer · Section drill (' + n + ')',
        'COMPUTER BOOK BANK (not PYQ) · ' + n + ' questions across all chapters · mode: Strict Exam');
      return true;
    }
    case 'csPyq': {
      var cc = csChapter(CS.ch);
      if (!cc) return true;
      practiceFromIds(csRelatedPyqs(cc).map(function (x) { return x.id; }),
        'Related PYQs · Computer Ch ' + cc.num, 'custom');
      return true;
    }
  }
  return false;
}

/* consistency check of the Computer bank, reported on the audit screen */
var CS_AUDIT = (function () {
  var errs = [], ids = {};
  CDATA.forEach(function (q) {
    if (ids[q.id]) errs.push(q.id + ': duplicate id');
    ids[q.id] = 1;
    if (!q.options || (q.options.length !== 4 && q.options.length !== 2)) errs.push(q.id + ': needs two or four options');
    if (!scorable(q) || q.correctAnswer < 0 || q.correctAnswer >= (q.options || []).length) errs.push(q.id + ': bad key');
    if (!q.explanation) errs.push(q.id + ': explanation missing');
    if (!q.examShortcut) errs.push(q.id + ': exam shortcut missing');
    if (!csChapter(q.csChapter)) errs.push(q.id + ': unknown chapter');
  });
  (CMETA ? CMETA.chapters : []).forEach(function (c) {
    var n = 0;
    c.sets.forEach(function (s) {
      var got = csSetQs(c.num, s.k).length;
      if (got !== s.n) errs.push('Chapter ' + c.num + ' set ' + s.k + ': ' + got + ' questions, meta says ' + s.n);
      n += got;
    });
    if (n !== c.n) errs.push('Chapter ' + c.num + ': sets hold ' + n + ' of ' + c.n + ' questions');
  });
  return { ok: !errs.length, errors: errs, total: CDATA.length };
})();
/* CS-JS-END */

/* ======================================================================
   CS.  COMPUTER  —  chapter-wise practice sets (11 chapters).
   Injected by computer-dashboard-src/integrate.py; edit it there, not here.
   The bank lives in window.csData / window.csMeta and is kept apart from
   the authentic PYQs: it never enters a year, sectional, topic, subtopic
   or custom PYQ mock, and the PYQ data audit ignores it.
   ====================================================================== */
var CS = { ch: 0, view: 'sets', bset: 1, ri: 0, pick: {}, open: {}, sheetOpen: 0, sheetAll: false };
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

/* the one clean line above a question: chapter · set · number */
function csMetaLine(q) {
  var c = csChapter(q.csChapter);
  return '<div class="qmeta cs-meta"><span class="cs-topic">' + E(c ? c.title : q.subtopic) + '</span>' +
    '<span>Set ' + q.csSet + '</span><span>' + E(q.csLabel) + '</span></div>';
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

/* the answer, in a fixed order: verdict -> Explanation -> Exam shortcut.
   The options above already show right and wrong in colour, so the
   verdict is a single line. */
function csRevealPanes(q, chosen, opts) {
  opts = opts || {};
  if (ROUTE.name === 'study') opts.peek = true;
  var answered = chosen !== null && chosen !== undefined;
  var ans = '<span class="ans">(' + LET[q.correctAnswer] + ') ' + csR(q.options[q.correctAnswer]) + '</span>';
  var h;
  if (!answered && opts.peek) h = '<div class="cs-verdict peek"><span class="ic">✓</span><span>Answer ' + ans + '</span></div>';
  else if (!answered) h = '<div class="cs-verdict skip"><span class="ic">–</span><span>Not answered · ' + ans + '</span></div>';
  else if (chosen === q.correctAnswer) h = '<div class="cs-verdict ok"><span class="ic">✓</span><span>Correct</span></div>';
  else h = '<div class="cs-verdict bad"><span class="ic">✗</span><span>Incorrect · answer ' + ans + '</span></div>';
  h += '<div class="cs-block cs-exp"><div class="lbl">Explanation</div><div class="tx">' + csR(q.explanation) + '</div></div>';
  h += '<div class="cs-block cs-short"><div class="lbl">Exam shortcut</div><div class="tx">' + csR(q.examShortcut) + '</div></div>';
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

/* chapter button: number, title and a coverage bar */
function csChapBtn(cc, act, on) {
  var cv = csCov(CS_BY_CH[cc.num] || []);
  return '<button type="button"' + (act === 'csCh' ? ' role="tab" aria-selected="' + on + '"' : '') +
    ' class="cs-tab' + (on ? ' on' : '') + '" data-act="' + act + '" data-ch="' + cc.num + '"><b>' + cc.num +
    '</b><span>' + E(cc.title) + '</span><i class="bar"><i style="width:' + fx(pct(cv.seen, cv.n), 1) + '%"></i></i></button>';
}

function csSetsView(c) {
  var rec = CsStore.d().sets;
  var next = null;
  c.sets.forEach(function (s) {
    if (next === null && !rec[c.num + '-' + s.k]) next = s.k;
  });
  var h = '<div class="cs-sets">';
  c.sets.forEach(function (s) {
    var qs = csSetQs(c.num, s.k);
    var r = rec[c.num + '-' + s.k];
    var sc = csCov(qs);
    h += '<div class="cs-set' + (s.k === next ? ' next' : '') + '">' +
      '<div class="hd"><b>Set ' + s.k + '</b><span class="rng">Q' + s.from + '–' + s.to + ' · ' + s.n + '</span>' +
      (s.k === next ? '<span class="chip brand">Next</span>' : '') + '<span class="sp"></span>' +
      (r ? '<span class="best">best ' + r.best + '%' + (r.bestExam !== null ? ' · exam ' + r.bestExam + '%' : '') + '</span>' : '') +
      '</div>' +
      (s.themes ? '<div class="themes">' + E(s.themes) + '</div>' : '') +
      '<div class="cov"><div class="progbar"><i class="' + (sc.seen === sc.n ? 'ok' : '') + '" style="width:' +
      fx(pct(sc.seen, sc.n), 1) + '%"></i></div><span>' + sc.seen + '/' + sc.n + '</span></div>' +
      '<div class="btnrow"><button type="button" class="btn sm primary" data-act="csStart" data-set="' + s.k +
      '" data-mode="learn">Learn</button><button type="button" class="btn sm" data-act="csStart" data-set="' + s.k +
      '" data-mode="exam">Exam</button><button type="button" class="btn sm ghost" data-act="csBrowse" data-set="' + s.k +
      '">Revise</button></div></div>';
  });
  h += '</div>';
  h += '<div class="card cs-whole"><b>Whole chapter</b><div class="btnrow">' +
    '<button type="button" class="btn sm" data-act="csChapterMock" data-mode="exam">All ' + c.n + ' · exam</button>' +
    '<button type="button" class="btn sm ghost" data-act="csChapterMock" data-mode="random">Random 20</button></div></div>';
  return h;
}

/* pointers: one fold-out section per heading, one open at a time */
function csSheetView(c) {
  var sh = csSheet(c.num);
  if (!sh) return '<div class="empty">No pointers for this chapter yet.</div>';
  var n = 0;
  sh.sections.forEach(function (s) { n += s.items.length; });
  var h = '<div class="cs-sheet-bar"><span class="small muted">' + n + ' points · <span class="hy">★</span> high-yield</span>' +
    '<span class="sp"></span><button type="button" class="btn sm ghost" data-act="csSheetAll">' +
    (CS.sheetAll ? 'Collapse all' : 'Expand all') + '</button>' +
    '<button type="button" class="btn sm ghost noprint" data-act="csPrint">Print</button></div><div class="cs-acc">';
  sh.sections.forEach(function (s, i) {
    var open = CS.sheetAll || CS.sheetOpen === i;
    h += '<details class="cs-sec"' + (open ? ' open' : '') + ' data-i="' + i + '"><summary><span class="k">' + (i + 1) +
      '</span><span class="t">' + E(s.title) + '</span><span class="n">' + s.items.length + '</span></summary><ul>';
    s.items.forEach(function (b) {
      h += '<li>' + csR(b).replace(/★/g, '<span class="hy" title="high-yield">★</span>') + '</li>';
    });
    h += '</ul></details>';
  });
  return h + '</div>';
}

/* revise: one question at a time, with a number strip to jump and
   Prev / Next (or a swipe) to move */
function csReviseView(c) {
  var k = Math.min(Math.max(1, CS.bset), c.sets.length);
  CS.bset = k;
  var qs = csSetQs(c.num, k);
  var i = Math.min(Math.max(0, CS.ri), qs.length - 1);
  CS.ri = i;
  var q = qs[i];
  var st = CsStore.d().q;
  var pick = CS.pick.hasOwnProperty(q.id) ? CS.pick[q.id] : null;
  var open = pick !== null || !!CS.open[q.id];
  var h = '<div class="card cs-rev"><div class="cs-pills" role="tablist" aria-label="Sets">';
  c.sets.forEach(function (s) {
    h += '<button type="button" role="tab" aria-selected="' + (s.k === k) + '" class="cs-pill' + (s.k === k ? ' on' : '') +
      '" data-act="csBrowse" data-set="' + s.k + '">Set ' + s.k + '</button>';
  });
  h += '</div><div class="cs-strip" aria-label="Questions">';
  qs.forEach(function (x, j) {
    var cls = 'cs-num' + (st.hasOwnProperty(x.id) ? (st[x.id] === 1 ? ' ok' : ' bad') : '') + (j === i ? ' cur' : '');
    h += '<button type="button" class="' + cls + '" data-act="csRi" data-i="' + j + '" aria-label="Question ' + (j + 1) + '">' +
      (j + 1) + '</button>';
  });
  h += '</div><div class="cs-rev-hd">' + csMetaLine(q) + bookmarkBtn(q.id) + '</div>' +
    '<div class="qtext">' + csBody(q) + '</div>' + csOptionList(q, pick);
  if (open) h += '<div class="reveal">' + csRevealPanes(q, pick, { peek: pick === null }) + '</div>';
  h += '<div class="cs-pager">' +
    '<button type="button" class="btn" data-act="csRi" data-d="-1" data-i="' + (i - 1) + '"' + (i === 0 ? ' disabled' : '') +
    '>‹ Prev</button>' +
    (open ? '<button type="button" class="btn mid" data-act="csHide" data-qid="' + E(q.id) + '">' +
            (pick !== null ? 'Try again' : 'Hide answer') + '</button>'
          : '<button type="button" class="btn mid" data-act="csShow" data-qid="' + E(q.id) + '">Show answer</button>') +
    '<button type="button" class="btn primary" data-act="csRi" data-d="1" data-i="' + (i + 1) + '"' +
    (i === qs.length - 1 ? ' disabled' : '') + '>Next ›</button></div>';
  return h + '</div>';
}

function csPyqView(c) {
  var rel = csRelatedPyqs(c);
  var h = '<div class="card"><div class="cs-pyqrow">';
  var ti = META.topicIntel || {};
  c.relCodes.forEach(function (k) {
    var n = DATA.filter(function (q) { return q.topicCode === k; }).length;
    h += '<span class="chip">' + E(ti[k] ? ti[k].name : k) + ' · ' + n + '</span>';
  });
  h += '</div><div class="btnrow"><button type="button" class="btn primary" data-act="csPyq"' +
    (rel.length ? '' : ' disabled') + '>Practise all ' + rel.length + '</button></div></div>';
  if (rel.length) {
    h += '<ul class="list">';
    rel.slice().sort(function (a, b) { return b.year - a.year || a.questionNumber - b.questionNumber; })
      .forEach(function (q) {
        h += '<li><div class="top"><span class="pyq-badge">' + q.year + ' Q' + q.questionNumber + '</span></div>' +
          '<div class="small">' + R(q.question) + '</div>' +
          '<div class="btnrow mt"><button type="button" class="btn sm ghost" data-act="study" data-qid="' + E(q.id) +
          '" data-back="cs">Study card</button></div></li>';
      });
    h += '</ul>';
  }
  return h;
}

V.cs = function () {
  if (!CMETA || !CDATA.length) {
    return crumb(['Home', 'Computer']) + '<div class="card"><h1>Computer bank not loaded</h1></div>';
  }
  var c = csChapter(CS.ch) || CMETA.chapters[0];
  CS.ch = c.num;
  var views = { sets: 'Sets', sheet: 'Pointers', read: 'Revise', pyq: 'PYQs' };
  if (!views[CS.view]) CS.view = 'sets';
  var h = crumb(['Home', 'Computer', 'Chapter ' + c.num, views[CS.view]]);

  var all = csCov(CDATA);
  var p = Math.round(pct(all.seen, all.n));
  h += '<div class="cs-top"><div class="cs-top-l"><h1>Computer</h1><span class="small muted">' + CMETA.total +
    ' questions · ' + CMETA.chapters.length + ' chapters · ' + CMETA.nSets + ' sets</span></div>' +
    '<div class="cs-ring" style="--p:' + p + '" title="Questions covered"><span>' + p + '%<small>done</small></span></div></div>';

  h += '<div class="cs-tabs" role="tablist" aria-label="Chapters">';
  CMETA.chapters.forEach(function (cc) { h += csChapBtn(cc, 'csCh', cc.num === c.num); });
  h += '</div>';

  var rel = csRelatedPyqs(c);
  var cv = csCov(CS_BY_CH[c.num] || []);
  h += '<div class="card cs-chap"><div class="cs-chap-hd"><h2>' + E(c.title) + '</h2><span class="small muted">Chapter ' +
    c.num + ' · ' + c.n + ' questions · ' + cv.seen + ' done</span></div>' +
    '<div class="cs-subtabs" role="tablist" aria-label="Chapter views">';
  [['sets', 'Sets', c.sets.length], ['sheet', 'Pointers', null], ['read', 'Revise', null], ['pyq', 'PYQs', rel.length]]
    .forEach(function (v) {
      var on = CS.view === v[0];
      h += '<button type="button" role="tab" aria-selected="' + on + '" class="cs-sub' + (on ? ' on' : '') +
        '" data-act="csView" data-v="' + v[0] + '">' + E(v[1]) + (v[2] !== null ? '<span class="n">' + v[2] + '</span>' : '') +
        '</button>';
    });
  h += '</div></div>';

  if (CS.view === 'sheet') h += csSheetView(c);
  else if (CS.view === 'read') h += csReviseView(c);
  else if (CS.view === 'pyq') h += csPyqView(c);
  else h += csSetsView(c);
  return h;
};

function csHomeSection() {
  if (!CMETA || !CDATA.length) return '';
  var all = csCov(CDATA);
  var h = '<h2 class="mt">Computer</h2><div class="card cs-home"><div class="cs-home-hd"><span>' + CMETA.total +
    ' questions · ' + CMETA.nSets + ' sets</span><span class="sp"></span><b>' +
    Math.round(pct(all.seen, all.n)) + '% done</b></div><div class="cs-tabs cs-grid">';
  CMETA.chapters.forEach(function (c) { h += csChapBtn(c, 'csGo', false); });
  h += '</div><div class="btnrow mt"><button type="button" class="btn sm" data-act="csGo" data-ch="' +
    CMETA.chapters[0].num + '" data-v="sheet">Pointers</button>' +
    '<button type="button" class="btn sm" data-act="csMix" data-n="20">Mixed drill · 20</button></div></div>';
  return h;
}

function csStartSet(k, mode) {
  var c = csChapter(CS.ch);
  if (!c) return;
  var qs = csSetQs(c.num, k);
  if (!qs.length) return;
  var st = Store.d().settings;
  var exam = mode === 'exam';
  var s = c.sets[k - 1];
  buildSession({
    kind: 'cs',
    name: csSetName(c.num, k),
    desc: 'Chapter ' + c.num + ' \u00b7 ' + c.title + ' \u00b7 Set ' + k + ' \u00b7 Q' + s.from + '\u2013' + s.to +
      ' \u00b7 ' + qs.length + ' questions \u00b7 ' + (exam ? 'Exam' : 'Learning'),
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

/* bring the answer into view once it opens, moving as little as possible */
function csShowReveal() {
  var r = app.querySelector('.cs-rev .reveal');
  if (r && r.scrollIntoView) r.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

/* accordion: opening one pointer section closes the others */
app.addEventListener('toggle', function (ev) {
  var d = ev.target;
  if (!d || !d.classList || !d.classList.contains('cs-sec')) return;
  var i = +d.getAttribute('data-i');
  if (d.open) {
    CS.sheetOpen = i;
    if (!CS.sheetAll) {
      Array.prototype.forEach.call(app.querySelectorAll('.cs-sec[open]'), function (o) { if (o !== d) o.open = false; });
      var sum = d.querySelector('summary');
      if (sum && sum.scrollIntoView) setTimeout(function () { sum.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }, 0);
    }
  } else if (CS.sheetOpen === i) CS.sheetOpen = -1;
}, true);

/* delegated clicks for this tab; returns true when handled */
function csClick(act, t) {
  var qid = t.getAttribute('data-qid');
  switch (act) {
    case 'csGo':
      CS.ch = +t.getAttribute('data-ch');
      CS.view = t.getAttribute('data-v') || 'sets';
      CS.bset = 1; CS.ri = 0; CS.sheetOpen = 0;
      go('cs');
      return true;
    case 'csCh':
      CS.ch = +t.getAttribute('data-ch'); CS.bset = 1; CS.ri = 0; CS.sheetOpen = 0;
      render();
      return true;
    case 'csView': CS.view = t.getAttribute('data-v'); render(); return true;
    case 'csBrowse':
      CS.view = 'read'; CS.bset = +t.getAttribute('data-set') || 1; CS.ri = 0;
      render();
      var rv = app.querySelector('.cs-rev');
      if (rv && rv.scrollIntoView) rv.scrollIntoView({ block: 'start' });
      return true;
    case 'csRi': {
      if (t.disabled) return true;
      CS.ri = +t.getAttribute('data-i');
      render();
      var card = app.querySelector('.cs-rev');
      if (card && card.getBoundingClientRect().top < 0) card.scrollIntoView({ block: 'start' });
      return true;
    }
    case 'csOpt': {
      var q = BY_ID[qid];
      var i = +t.getAttribute('data-i');
      CS.pick[qid] = i;
      if (q) csMarkQ(qid, i === q.correctAnswer);
      render(); csShowReveal();
      return true;
    }
    case 'csShow': CS.open[qid] = true; render(); csShowReveal(); return true;
    case 'csHide': delete CS.open[qid]; delete CS.pick[qid]; render(); return true;
    case 'csSheetAll': CS.sheetAll = !CS.sheetAll; if (!CS.sheetAll) CS.sheetOpen = 0; render(); return true;
    case 'csPrint': {
      var was = CS.sheetAll;
      CS.sheetAll = true; render();
      window.print();
      CS.sheetAll = was; render();
      return true;
    }
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
        csStartPool(qs.slice(0, 20), 'Computer \u00b7 Ch ' + c.num + ' \u00b7 Random 20',
          'Chapter ' + c.num + ' \u00b7 ' + c.title + ' \u00b7 20 random questions \u00b7 Exam');
      } else {
        csStartPool(qs, 'Computer \u00b7 Ch ' + c.num + ' \u00b7 Whole chapter',
          'Chapter ' + c.num + ' \u00b7 ' + c.title + ' \u00b7 all ' + qs.length + ' questions \u00b7 Exam');
      }
      return true;
    }
    case 'csMix': {
      var n = +t.getAttribute('data-n') || 20;
      var pool = CDATA.slice();
      shuffle(pool);
      csStartPool(pool.slice(0, n), 'Computer \u00b7 Mixed drill (' + n + ')',
        'All chapters \u00b7 ' + n + ' questions \u00b7 Exam');
      return true;
    }
    case 'csPyq': {
      var cc = csChapter(CS.ch);
      if (!cc) return true;
      practiceFromIds(csRelatedPyqs(cc).map(function (x) { return x.id; }),
        'PYQs \u00b7 Computer Ch ' + cc.num, 'custom');
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

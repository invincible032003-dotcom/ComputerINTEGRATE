/* ------------------------------------------------ Android / mobile shell
   Injected by computer-dashboard-src/integrate.py; edit it there.
   Adds the bottom navigation bar, the in-session action bar with a pop-up
   palette sheet, a screen title in the top bar, swipe between questions,
   and Android back-button support (browser history). Every control proxies
   to the dashboard's own buttons, so the app logic is unchanged; on
   desktop the bars stay hidden by CSS. */
var MOB_ICON = {
  home: 'M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5.5h-5V20H5a1 1 0 0 1-1-1z',
  cs: 'M3 5h18v11H3zM8.5 20h7M12 16v4',
  gk: 'M3 5h6a3 3 0 0 1 3 3v12a2.5 2.5 0 0 0-2.5-2.5H3zM21 5h-6a3 3 0 0 0-3 3v12a2.5 2.5 0 0 1 2.5-2.5H21z',
  search: 'M10.5 4a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13zM20 20l-4.8-4.8',
  prev: 'M15 5l-7 7 7 7', next: 'M9 5l7 7-7 7',
  mark: 'M6 4h12v16l-6-4-6 4z', grid: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  done: 'M5 12.5l4.5 4.5L19 7'
};
var MOB_NAV = [['home', 'Home'], ['cs', 'Computer'], ['gk', 'G&K'], ['search', 'Search']];

function mobSvg(k) {
  return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + MOB_ICON[k] + '"/></svg>';
}

function mobLeaveSession() {
  if (S && !S.finished && ROUTE.name === 'exam') {
    if (!window.confirm('Leave the mock in progress? Your answers will be lost.')) return false;
    stopTick(); S = null;
  }
  return true;
}

var MOB_TITLES = { home: 'Offline Mock Engine', cs: 'Computer', gk: 'Gupta Kapoor', search: 'Search' };
var mobRevSeen = {};

function mobPalette(open) {
  document.body.classList.toggle('pal-open', !!open);
}

function mobSync() {
  var r = ROUTE.name;
  mobPalette(false);
  /* top app bar: the name of the current screen */
  var tt = document.querySelector('#topbar .mtitle');
  if (tt) {
    var title = MOB_TITLES[r];
    if (!title && S && (r === 'exam' || r === 'result' || r === 'review')) title = S.name + (r === 'exam' ? '' : ' \u00b7 ' + (r === 'result' ? 'Result' : 'Review'));
    if (!title) { var cb = app.querySelector('.crumb b'); title = cb ? cb.textContent : 'Offline Mock Engine'; }
    tt.textContent = title;
  }
  var active = (r === 'cs' || r === 'gk' || r === 'search') ? r : 'home';
  if ((r === 'exam' || r === 'result' || r === 'review') && S) {
    active = S.kind === 'cs' ? 'cs' : S.kind === 'gk' ? 'gk' : 'home';
  }
  var nav = document.getElementById('bnav');
  if (nav) {
    Array.prototype.forEach.call(nav.querySelectorAll('button'), function (b) {
      var on = b.getAttribute('data-r') === active;
      b.classList.toggle('on', on);
      if (on) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
    });
  }
  var live = r === 'exam' && S && !S.finished;
  document.body.classList.toggle('in-session', !!live);
  var bar = document.getElementById('msess');
  if (bar && live) {
    var last = S.cur === S.items.length - 1;
    bar.innerHTML =
      '<button type="button" data-proxy="prevQ" aria-label="Previous question"' + (S.cur === 0 ? ' disabled' : '') + '>' +
        mobSvg('prev') + '<span class="lbl">Prev</span></button>' +
      '<button type="button" data-proxy="markQ" class="' + (S.marked[S.cur] ? 'on' : '') + '" aria-pressed="' +
        !!S.marked[S.cur] + '" aria-label="Mark for review">' + mobSvg('mark') + '<span class="lbl">Mark</span></button>' +
      '<button type="button" data-proxy="palette" aria-label="Question palette">' + mobSvg('grid') +
        '<span class="pos">' + (S.cur + 1) + '/' + S.items.length + '</span></button>' +
      (last ? '<button type="button" data-proxy="submitMock" class="pri">' + mobSvg('done') + 'Submit</button>'
            : '<button type="button" data-proxy="nextQ" class="pri">Next' + mobSvg('next') + '</button>');
  }
  /* learning mode: the first time an answer opens, bring it into view */
  if (live && S.mode === 'learn' && S.revealed[S.cur]) {
    var key = S.startTs + ':' + S.cur;
    if (!mobRevSeen[key]) {
      mobRevSeen[key] = 1;
      var rv = app.querySelector('.reveal');
      if (rv && rv.scrollIntoView) rv.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }
  /* keep the selected chip of every scrolling row in view */
  [['.cs-tabs', '.cs-tab.on'], ['.cs-pills', '.cs-pill.on'], ['.cs-strip', '.cs-num.cur']].forEach(function (p) {
    var row = app.querySelector(p[0]);
    var on = row && row.querySelector(p[1]);
    if (on && row.scrollWidth > row.clientWidth) {
      row.scrollLeft = Math.max(0, on.offsetLeft - row.offsetLeft - (row.clientWidth - on.offsetWidth) / 2);
    }
  });
}

(function mobShell() {
  var brand = document.querySelector('#topbar .brand');
  if (brand) {
    var tt = document.createElement('span');
    tt.className = 'mtitle';
    tt.textContent = 'Offline Mock Engine';
    brand.insertBefore(tt, brand.firstChild);
  }

  var nav = document.createElement('nav');
  nav.id = 'bnav';
  nav.setAttribute('aria-label', 'Main');
  nav.innerHTML = MOB_NAV.map(function (n) {
    return '<button type="button" data-r="' + n[0] + '"><span class="ic">' + mobSvg(n[0]) + '</span>' + E(n[1]) + '</button>';
  }).join('');
  document.body.appendChild(nav);
  nav.addEventListener('click', function (ev) {
    var t = closest(ev.target, '[data-r]');
    if (!t || !mobLeaveSession()) return;
    go(t.getAttribute('data-r'));
  });

  var bar = document.createElement('div');
  bar.id = 'msess';
  bar.setAttribute('role', 'toolbar');
  bar.setAttribute('aria-label', 'Question navigation');
  document.body.appendChild(bar);
  bar.addEventListener('click', function (ev) {
    var t = closest(ev.target, '[data-proxy]');
    if (!t || t.disabled) return;
    var a = t.getAttribute('data-proxy');
    if (a === 'palette') { mobPalette(!document.body.classList.contains('pal-open')); return; }
    var b = app.querySelector('[data-act="' + a + '"]');
    if (b && !b.disabled) b.click();
  });

  var scrim = document.createElement('div');
  scrim.id = 'mscrim';
  document.body.appendChild(scrim);
  scrim.addEventListener('click', function () { mobPalette(false); });

  if (window.MutationObserver) new MutationObserver(mobSync).observe(app, { childList: true });

  /* swipe left / right between questions (mock) and review steps */
  var sx = 0, sy = 0, st = 0, ok = false;
  app.addEventListener('touchstart', function (e) {
    ok = e.touches.length === 1 &&
      !closest(e.target, 'pre, table, .cs-code, .scrollx, .cs-tabs, .cs-subtabs, .cs-pills, .cs-strip, .exam-side, ' +
        '.katex-display, input, textarea, select');
    if (!ok) return;
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now();
  }, { passive: true });
  app.addEventListener('touchend', function (e) {
    if (!ok) return;
    ok = false;
    var t = e.changedTouches[0];
    var dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.abs(dx) < 70 || Math.abs(dy) > Math.abs(dx) * 0.6 || Date.now() - st > 800) return;
    var fwd = dx < 0;
    var b = null;
    if (ROUTE.name === 'exam' && S && !S.finished) b = app.querySelector('[data-act="' + (fwd ? 'nextQ' : 'prevQ') + '"]');
    else if (ROUTE.name === 'review') b = app.querySelector('[data-act="revStep"][data-d="' + (fwd ? '1' : '-1') + '"]');
    else if (ROUTE.name === 'cs' && CS.view === 'read') b = app.querySelector('.cs-pager [data-d="' + (fwd ? '1' : '-1') + '"]');
    if (b && !b.disabled) b.click();
  }, { passive: true });

  /* Android back button: every go() becomes a history entry */
  var baseGo = go;
  go = function (name, params) {
    baseGo(name, params);
    try { history.pushState({ iss: 1, r: ROUTE }, ''); } catch (e) {}
  };
  try { history.replaceState({ iss: 1, r: { name: 'home' } }, ''); } catch (e) {}
  window.addEventListener('popstate', function (ev) {
    if (document.body.classList.contains('pal-open')) {
      mobPalette(false);
      try { history.pushState({ iss: 1, r: ROUTE }, ''); } catch (e) {}
      return;
    }
    if (!mobLeaveSession()) {
      try { history.pushState({ iss: 1, r: ROUTE }, ''); } catch (e) {}
      return;
    }
    var r = ev.state && ev.state.r ? ev.state.r : { name: 'home' };
    if (r.name === 'exam') r = { name: S && S.finished ? 'result' : 'home' };
    if ((r.name === 'result' || r.name === 'review') && !(S && S.finished)) r = { name: 'home' };
    ROUTE = r;
    render();
    window.scrollTo(0, 0);
  });
})();

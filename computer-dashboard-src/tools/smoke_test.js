// Headless smoke test of the Computer tab.
// usage: NODE_PATH=$(npm root -g) node tools/smoke_test.js <html> <outdir>
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const file = path.resolve(process.argv[2]);
  const out = process.argv[3] || '.';
  const browser = await chromium.launch();
  const errors = [];
  const check = async (page, label) => {
    const w = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    if (w[0] > w[1] + 1) errors.push(`${label}: horizontal overflow ${w[0]} > ${w[1]}`);
  };
  for (const [name, vp] of [['desktop', { width: 1280, height: 900 }], ['phone', { width: 360, height: 800 }]]) {
    const page = await browser.newPage({ viewport: vp });
    page.on('pageerror', e => errors.push(`${name} pageerror: ${e.message}`));
    page.on('console', m => { if (m.type() === 'error') errors.push(`${name} console: ${m.text()}`); });
    page.on('dialog', d => d.accept());
    await page.goto('file://' + file);
    await page.waitForSelector('#app .card');
    const info = await page.evaluate(() => ({ cs: window.ISSApp.cs.total, audit: window.ISSApp.cs.audit }));
    if (name === 'desktop') console.log('bank', info.cs, 'audit ok', info.audit.ok, info.audit.errors.slice(0, 5));
    await page.screenshot({ path: `${out}/${name}-home.png`, fullPage: false });
    const nav = name === 'phone' ? '#bnav' : '#topbar';
    // phones submit from the palette sheet
    const submit = async pg => {
      if (name === 'phone') {
        await pg.click('#msess [data-proxy="palette"]');
        await pg.click('.pal-actions [data-act="submitMock"]');
      } else await pg.click('.exam-actions [data-act="submitMock"]');
    };
    await page.click(nav + ' [data-r="cs"]');
    await page.waitForSelector('.cs-tabs');
    await check(page, name + ' cs');
    await page.screenshot({ path: `${out}/${name}-cs.png`, fullPage: true });
    // pointers: fold-out sections, one open at a time
    await page.click('[data-act="csView"][data-v="sheet"]');
    await page.click('.cs-sec[data-i="2"] > summary');
    await page.waitForTimeout(150);
    const open = await page.evaluate(() => [].map.call(document.querySelectorAll('.cs-sec[open]'), d => d.getAttribute('data-i')).join());
    if (open !== '2') errors.push(`${name} sheet: open sections "${open}", expected "2"`);
    await check(page, name + ' sheet');
    await page.screenshot({ path: `${out}/${name}-sheet.png`, fullPage: true });
    // revise: one question at a time
    await page.click('[data-act="csView"][data-v="read"]');
    await page.click('.cs-rev [data-act="csOpt"][data-i="1"]');
    await page.waitForSelector('.cs-rev .cs-short');
    await page.click('.cs-pager [data-d="1"]');
    await page.click('.cs-num:nth-child(10)');
    const pos = await page.evaluate(() => document.querySelector('.cs-num.cur').textContent);
    if (pos !== '10') errors.push(`${name} revise: at question ${pos}, expected 10`);
    await check(page, name + ' revise');
    await page.screenshot({ path: `${out}/${name}-read.png` });
    // learning session on set 1
    await page.click('[data-act="csView"][data-v="sets"]');
    await page.click('.cs-set [data-act="csStart"][data-mode="learn"]');
    await page.waitForSelector('.exam-head');
    await page.click('.opts [data-act="opt"][data-i="0"]');
    await page.waitForSelector('.cs-exp');
    await check(page, name + ' learn');
    await page.screenshot({ path: `${out}/${name}-learn.png`, fullPage: true });
    await page.click(name === 'phone' ? '#msess [data-proxy="nextQ"]' : '[data-act="nextQ"]');
    await page.keyboard.press('2');
    await submit(page);
    await page.waitForSelector('.kpis');
    await page.screenshot({ path: `${out}/${name}-result.png`, fullPage: false });
    await page.click('[data-act="reviewAt"][data-i="0"]');
    await page.waitForSelector('.cs-short');
    await page.click(nav + ' [data-r="cs"]');
    await page.waitForSelector('.cs-set');
    // exam session on chapter 2 set 2
    await page.click('[data-act="csCh"][data-ch="2"]');
    await page.click('.cs-set:nth-child(2) [data-act="csStart"][data-mode="exam"]');
    await page.waitForSelector('#timer');
    await page.keyboard.press('3');
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('1');
    await page.screenshot({ path: `${out}/${name}-exam.png` });
    await submit(page);
    await page.waitForSelector('.kpis');
    const prog = await page.evaluate(() => localStorage.getItem('upsc.iss.cs.v1'));
    if (name === 'desktop') console.log('progress', prog && prog.slice(0, 200));
    // search + audit
    await page.click(nav + ' [data-r="search"]');
    await page.selectOption('[data-act="searchBank"]', 'cs');
    await page.fill('#sq', 'binary');
    await page.waitForTimeout(400);
    await check(page, name + ' search');
    await page.goto('file://' + file);
    await page.evaluate(() => { document.querySelector('[data-r="audit"]') && 0; });
    await page.close();
  }
  await browser.close();
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
})();

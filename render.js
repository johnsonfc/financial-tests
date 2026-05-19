const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/pitchbook.html', { waitUntil: 'load' });
  await page.pdf({
    path: __dirname + '/smci_pitchbook_2026-05-19.pdf',
    width: '11in', height: '8.5in',
    landscape: true, printBackground: true,
    margin: { top: 0, bottom: 0, left: 0, right: 0 }
  });
  await browser.close();
  console.log('PDF written');
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });

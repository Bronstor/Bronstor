// Uso: node render.js entrada.(html|svg) salida.png ancho alto [escala] [transparente]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
(async () => {
  const [inp, out, w, h, scale = '1', transp = '0'] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: +w, height: +h },
    deviceScaleFactor: +scale,
  });
  await page.goto('file://' + path.resolve(inp));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(150);
  await page.screenshot({ path: out, omitBackground: transp === '1' });
  await browser.close();
})();

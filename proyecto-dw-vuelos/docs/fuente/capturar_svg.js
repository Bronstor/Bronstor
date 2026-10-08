// Convierte un archivo SVG en PNG con Chromium (Playwright).
// Uso: node capturar_svg.js entrada.svg salida.png ancho_px
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const [entrada, salida, ancho] = process.argv.slice(2);
  if (!entrada || !salida) {
    console.error('Uso: node capturar_svg.js entrada.svg salida.png [ancho_px]');
    process.exit(1);
  }
  const w = parseInt(ancho || '1600', 10);
  const svg = fs.readFileSync(entrada, 'utf8');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w + 40, height: 1200 }, deviceScaleFactor: 2 });
  await page.setContent(
    `<!doctype html><html><body style="margin:0;background:#fff">` +
    `<div id="d" style="width:${w}px">${svg}</div></body></html>`,
  );
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => {
    const s = document.querySelector('#d svg');
    s.style.width = '100%';
    s.style.height = 'auto';
    s.style.display = 'block';
  });
  await page.locator('#d svg').screenshot({ path: salida });
  await browser.close();
})();

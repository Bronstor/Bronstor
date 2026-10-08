// Convierte el informe HTML en PDF con Chromium (Playwright).
// Uso: node imprimir_pdf.js entrada.html salida.pdf
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [entrada, salida] = process.argv.slice(2);
  if (!entrada || !salida) {
    console.error('Uso: node imprimir_pdf.js entrada.html salida.pdf');
    process.exit(1);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(entrada), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: salida,
    preferCSSPageSize: true,
    printBackground: true,
    displayHeaderFooter: false,
  });
  await browser.close();
})();

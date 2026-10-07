// node capture.js video.html framesDir fps [soloTiempos...]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const [inp, dir, fps, ...only] = process.argv.slice(2);
  fs.mkdirSync(dir, { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(inp));
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
  const total = await page.evaluate(() => window.TOTAL);
  const times = only.length ? only.map(Number) : [...Array(Math.round(total * fps)).keys()].map(i => i / fps);
  let k = 0;
  for (const t of times) {
    await page.evaluate(t => render(t), t);
    const name = only.length ? `t${t}.png` : `f${String(k).padStart(5, '0')}.jpg`;
    await page.screenshot({ path: path.join(dir, name), type: only.length ? 'png' : 'jpeg', quality: only.length ? undefined : 94 });
    k++;
  }
  await browser.close();
  console.log('frames', k, 'total', total);
})();

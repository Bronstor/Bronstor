import os, subprocess
from routes import cota, K, W, R
from cota_sys import strip, avatar

OUT = '/home/user/Bronstor/marca/rediseno/logo'
os.makedirs(OUT + '/svg', exist_ok=True); os.makedirs(OUT + '/png', exist_ok=True)
os.makedirs(OUT + '/para-gemini', exist_ok=True)
RENDER = os.path.join(os.path.dirname(__file__), '..', 'build', 'render.js')

def svg(body, bounds, pad, bg=None):
    x0, y0, x1, y1 = bounds
    w, h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    r = f'<rect x="{x0 - pad:.1f}" y="{y0 - pad:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0 - pad:.1f} {y0 - pad:.1f} {w:.1f} {h:.1f}" '
            f'width="{w:.0f}" height="{h:.0f}">{r}{body}</svg>'), w, h

def write(path_base, body, bounds, pad, bg=None, width_px=2400, transparent=False):
    s, w, h = svg(body, bounds, pad, bg)
    p = path_base + '.svg'
    open(p, 'w').write(s)
    return p, w, h

def png(svg_path, png_path, w, h, width_px=2400, transparent=False):
    sc = width_px / w
    subprocess.run(['node', RENDER, svg_path, png_path, str(int(round(w))), str(int(round(h))), f'{sc:.4f}', '1' if transparent else '0'], check=True)

# --- logo completo (palabra + cota), sin descriptor
body_k, b_k = cota(K, descriptor=False)
body_w, b_w = cota(W, descriptor=False)
# --- cinta
sb_k = strip(K, R, 100, 560); sb_w = strip(W, R, 100, 560)
b_s = (0, -50, 560, 50)
# --- símbolo cuadrado
av_k, _ = avatar('#111111', W, R, 400)

jobs = [
  ('logo-completo-positivo', body_k, b_k, 60, None, True),
  ('logo-completo-negativo', body_w, b_w, 60, None, True),
  ('cinta-EM-positivo', sb_k, b_s, 40, None, True),
  ('cinta-EM-negativo', sb_w, b_s, 40, None, True),
]
for name, body, b, pad, bg, tr in jobs:
    p, w, h = write(f'{OUT}/svg/{name}', body, b, pad, bg)
    png(p, f'{OUT}/png/{name}.png', w, h, 2400, True)

# --- archivos para Gemini: fondo sólido
G = f'{OUT}/para-gemini'
for name, body, b, pad, bg in [
    ('1-cinta-EM-sobre-negro', sb_w, b_s, 90, '#111111'),
    ('2-logo-completo-sobre-negro', body_w, b_w, 110, '#111111'),
    ('3-logo-completo-sobre-blanco', body_k, b_k, 110, '#FFFFFF'),
]:
    s, w, h = svg(body, b, pad, bg)
    p = f'/tmp/claude-0/-home-user-Bronstor/89cd71e1-c250-5f27-8781-54bae2f02ca7/scratchpad/build2/{name}.svg'
    open(p, 'w').write(s)
    png(p, f'{G}/{name}.png', w, h, 2000, False)
# símbolo cuadrado
s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">{av_k}</svg>'
p = '/tmp/claude-0/-home-user-Bronstor/89cd71e1-c250-5f27-8781-54bae2f02ca7/scratchpad/build2/sym.svg'
open(p, 'w').write(s)
png(p, f'{G}/4-simbolo-cuadrado-negro.png', 400, 400, 1200, False)
open(f'{OUT}/svg/simbolo-cuadrado-negro.svg', 'w').write(s)
print('ok')

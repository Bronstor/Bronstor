"""Genera el sistema de logo de Multirepuesto E&M como SVG 100% vectorial (sin fuentes)."""
import math
import os
from textpath import text_path

R = '#D7141A'   # Rojo E&M
K = '#111111'   # Negro carbón
W = '#FFFFFF'
SK = 0.21       # inclinación (~12°)
OUT = os.path.join(os.path.dirname(__file__), 'out', 'logo')
os.makedirs(OUT, exist_ok=True)


def rhex(cx, cy, r, rc):
    """Hexágono (vértices a izquierda y derecha) con esquinas redondeadas, como path."""
    v = [(cx + r * math.cos(math.radians(60 * i)), cy + r * math.sin(math.radians(60 * i))) for i in range(6)]
    t = rc / math.tan(math.radians(60))
    d = []
    for i in range(6):
        p, c, n = v[i - 1], v[i], v[(i + 1) % 6]
        def toward(a, b):
            L = math.dist(a, b)
            return (a[0] + (b[0] - a[0]) / L * t, a[1] + (b[1] - a[1]) / L * t)
        pin, pout = toward(c, p), toward(c, n)
        d.append(('M' if i == 0 else 'L') + '%.2f %.2f' % pin)
        d.append('A%.2f %.2f 0 0 1 %.2f %.2f' % (rc, rc, *pout))
    return ''.join(d) + 'Z'


def union(bs):
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


def monogram(size, col_letters, col_amp):
    """E & M inclinado, centrado ópticamente en (0,0). Devuelve markup."""
    g = size * 0.035
    dE, wE, bE = text_path('ArchivoExpBlack.ttf', 'E', size, 0, 0, skew=SK)
    _, wA, _ = text_path('ArchivoBold.ttf', '&', size * 0.6, 0, 0, skew=SK)
    xA = wE + g
    xM = xA + wA + g
    dA, _, bA = text_path('ArchivoBold.ttf', '&', size * 0.6, xA, 0, skew=SK)
    dM, _, bM = text_path('ArchivoExpBlack.ttf', 'M', size, xM, 0, skew=SK)
    b = union([bE, bA, bM])
    # bounds de fontTools están en coords de fuente transformadas => y ya invertida
    cx = (b[0] + b[2]) / 2
    cy = (b[1] + b[3]) / 2
    return (f'<g transform="translate({-cx:.2f},{-cy:.2f})">'
            f'<path d="{dE}" fill="{col_letters}"/><path d="{dA}" fill="{col_amp}"/>'
            f'<path d="{dM}" fill="{col_letters}"/></g>')


# Símbolo: radio exterior 124 => ancho ~248, alto ~215
SYM_W, SYM_H = 248, 2 * 124 * math.sin(math.radians(60))


def symbol(variant='principal'):
    """Markup del símbolo centrado en (0,0)."""
    if variant == 'principal':      # tuerca roja, centro negro
        return (f'<path d="{rhex(0, 0, 124, 14)}" fill="{R}"/>'
                f'<path d="{rhex(0, 0, 100, 8)}" fill="{K}"/>' + monogram(64, W, R))
    if variant == 'rojo':           # sólido rojo (bordado simple / tamaños pequeños)
        return f'<path d="{rhex(0, 0, 124, 14)}" fill="{R}"/>' + monogram(70, W, W)
    if variant == 'negro':          # una tinta negra
        return f'<path d="{rhex(0, 0, 124, 14)}" fill="{K}"/>' + monogram(70, W, W)
    if variant == 'blanco':         # una tinta blanca (sobre fondos oscuros), letras caladas
        return (f'<mask id="m"><rect x="-200" y="-200" width="400" height="400" fill="#fff"/>'
                f'{monogram(70, "#000", "#000")}</mask>'
                f'<path d="{rhex(0, 0, 124, 14)}" fill="{W}" mask="url(#m)"/>')
    raise ValueError(variant)


def wordmark(size, col_main, col_sub):
    """MULTIREPUESTO + línea E & M · AUTOPARTES. Origen arriba-izquierda. Devuelve (markup, w, h)."""
    d1, w1, b1 = text_path('ArchivoExpBlack.ttf', 'MULTIREPUESTO', size, 0, 0, skew=SK, tracking=-0.01)
    cap = -b1[1]  # alto de mayúsculas (aprox)
    base1 = cap - b1[3] if False else cap
    d1, w1, b1 = text_path('ArchivoExpBlack.ttf', 'MULTIREPUESTO', size, 0, cap, skew=SK, tracking=-0.01)
    sub = size * 0.30
    gap = size * 0.34
    sub_cap = sub * 0.72
    base2 = cap + gap + sub_cap
    bar_w = size * 0.5
    bar_h = sub * 0.42
    bar_y = base2 - sub_cap / 2 - bar_h / 2
    bx = bar_w + size * 0.30
    # el texto inferior (espaciado fijo 0.22em) se escala para terminar alineado con MULTIREPUESTO
    target = w1 - bx - size * 0.04
    _, w_1, _ = text_path('ArchivoBold.ttf', 'E & M  ·  AUTOPARTES', 100, 0, 0, skew=SK, tracking=0.30)
    sub = 100 * target / w_1
    sub_cap = sub * 0.72
    base2 = cap + gap + sub_cap
    bar_h = sub * 0.36
    bar_y = base2 - sub_cap / 2 - bar_h / 2
    d2, w2, b2 = text_path('ArchivoBold.ttf', 'E & M  ·  AUTOPARTES', sub, bx, base2, skew=SK, tracking=0.30)
    sk_off = SK * (base2 - bar_y)  # desplazar barra según inclinación
    bar = (f'<path d="M{sk_off + SK * bar_h:.2f} {bar_y:.2f}h{bar_w:.2f}l{-SK * bar_h:.2f} {bar_h:.2f}'
           f'h{-bar_w:.2f}z" fill="{R}"/>')
    markup = f'<path d="{d1}" fill="{col_main}"/>{bar}<path d="{d2}" fill="{col_sub}"/>'
    return markup, w1, base2


def svg(w, h, body, pad=0, bg=None):
    bgr = f'<rect x="{-pad}" y="{-pad}" width="{w + 2 * pad}" height="{h + 2 * pad}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad:.2f} {h + 2 * pad:.2f}" '
            f'width="{w + 2 * pad:.0f}" height="{h + 2 * pad:.0f}">{bgr}{body}</svg>')


def horizontal(dark=False, variant='principal'):
    col = W if dark else K
    sub = W if dark else K
    wsize = 92
    wm, ww, wh = wordmark(wsize, col, sub)
    s = 1.0
    gap = 54
    total_w = SYM_W + gap + ww
    h = SYM_H
    body = (f'<g transform="translate({SYM_W / 2},{SYM_H / 2})">{symbol(variant)}</g>'
            f'<g transform="translate({SYM_W + gap},{(SYM_H - wh) / 2:.2f})">{wm}</g>')
    return total_w, h, body


def vertical(dark=False, variant='principal'):
    col = W if dark else K
    wsize = 64
    wm, ww, wh = wordmark(wsize, col, col)
    gap = 46
    w = max(ww, SYM_W)
    h = SYM_H + gap + wh
    body = (f'<g transform="translate({w / 2},{SYM_H / 2})">{symbol(variant)}</g>'
            f'<g transform="translate({(w - ww) / 2:.2f},{SYM_H + gap})">{wm}</g>')
    return w, h, body


def write(name, w, h, body, pad):
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write(svg(w, h, body, pad=pad))


if __name__ == '__main__':
    P = 30
    for v in ['principal', 'rojo', 'negro', 'blanco']:
        write(f'simbolo-{v}', SYM_W, SYM_H, f'<g transform="translate({SYM_W / 2},{SYM_H / 2})">{symbol(v)}</g>', P)
    write('logo-horizontal', *horizontal(False), P)
    write('logo-horizontal-negativo', *horizontal(True), P)
    write('logo-vertical', *vertical(False), P)
    write('logo-vertical-negativo', *vertical(True), P)
    w, h, b = horizontal(False, 'negro'); write('logo-horizontal-1tinta-negro', w, h, b.replace(R, K), P)
    w, h, b = horizontal(True, 'blanco'); write('logo-horizontal-1tinta-blanco', w, h, b.replace(R, W), P)
    print('ok')

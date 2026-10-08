"""Tres rutas de identidad para Multirepuesto E&M, concepto 'la pieza exacta'."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'build'))
from textpath import text_path

R = '#D7141A'
K = '#111111'
W = '#FFFFFF'
G = '#6B6F76'
BOLD = 'BarlowSC-Bold.ttf'
MED = 'BarlowSC-Medium.ttf'
XB = 'BarlowC-ExtraBold.ttf'
MONO = 'PlexMono.ttf'


def tp(font, t, size, x=0, y=0, tracking=0.0, anchor='start', fill=K):
    d, w, b = text_path(font, t, size, x, y, anchor=anchor, tracking=tracking)
    return f'<path d="{d}" fill="{fill}"/>', w, b


# ---------------------------------------------------------------- RUTA 1 · COTA
def cota(fg=K, accent=R, size=150, descriptor=True):
    """Palabra MULTIREPUESTO con una línea de cota (medida) cuyo valor es E&M."""
    word, w, b = tp(BOLD, 'MULTIREPUESTO', size, 0, 0, tracking=0.035, fill=fg)
    x0, x1 = b[0], b[2]
    top, base = b[1], b[3]
    cap = base - top
    ly = base + cap * 0.62                      # altura de la línea de cota
    th = cap * 0.30                             # mitad del alto de las marcas
    sw = max(size * 0.022, 2.5)
    al, ah = size * 0.17, size * 0.065          # largo y media altura de la flecha
    label, lw, lb = tp(XB, 'E&M', size * 0.40, (x0 + x1) / 2, ly + size * 0.40 * 0.36, tracking=0.04, anchor='middle', fill=accent)
    gap = size * 0.10
    lx0, lx1 = (x0 + x1) / 2 - lw / 2 - gap, (x0 + x1) / 2 + lw / 2 + gap
    g = [word,
         f'<line x1="{x0:.2f}" y1="{ly - th:.2f}" x2="{x0:.2f}" y2="{ly + th:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<line x1="{x1:.2f}" y1="{ly - th:.2f}" x2="{x1:.2f}" y2="{ly + th:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<line x1="{x0 + al * 0.9:.2f}" y1="{ly:.2f}" x2="{lx0:.2f}" y2="{ly:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<line x1="{lx1:.2f}" y1="{ly:.2f}" x2="{x1 - al * 0.9:.2f}" y2="{ly:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<polygon points="{x0 + sw / 2:.2f},{ly:.2f} {x0 + sw / 2 + al:.2f},{ly - ah:.2f} {x0 + sw / 2 + al:.2f},{ly + ah:.2f}" fill="{accent}"/>',
         f'<polygon points="{x1 - sw / 2:.2f},{ly:.2f} {x1 - sw / 2 - al:.2f},{ly - ah:.2f} {x1 - sw / 2 - al:.2f},{ly + ah:.2f}" fill="{accent}"/>',
         label]
    h_end = ly + th
    if descriptor:
        ds, dw, db = tp(MONO, 'REPUESTOS Y AUTOPARTES · TODAS LAS MARCAS', size * 0.105, x0, h_end + size * 0.30, tracking=0.12, fill=G)
        g.append(ds)
        h_end += size * 0.30
    return ''.join(g), (x0, top, x1, h_end)


# ---------------------------------------------------------------- RUTA 2 · ETIQUETA
def tag_path(x, y, w, h, c):
    """Etiqueta de repuesto: esquinas izquierdas cortadas y orificio."""
    return (f'M{x + c:.1f} {y:.1f} H{x + w:.1f} V{y + h:.1f} H{x + c:.1f} L{x:.1f} {y + h - c:.1f} '
            f'V{y + c:.1f} Z')


def etiqueta(fg=K, tagfill=K, tagtext=W, accent=R, size=1.0, hole_bg=W):
    w, h, c = 330 * size, 200 * size, 46 * size
    d = tag_path(0, 0, w, h, c)
    hx, hy, hr = 62 * size, h / 2, 17 * size
    g = [f'<path d="{d}" fill="{tagfill}"/>',
         f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hr * 1.9:.1f}" fill="none" stroke="{accent}" stroke-width="{4 * size:.1f}"/>',
         f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hr:.1f}" fill="{hole_bg}"/>']
    em, ew, eb = tp(XB, 'E&M', 118 * size, 112 * size, hy + 40 * size, tracking=0.02, fill=tagtext)
    g.append(em)
    ref, rw, rb = tp(MONO, 'REF. 0001', 15 * size, 114 * size, h - 26 * size, tracking=0.12, fill=accent)
    g.append(ref)
    return ''.join(g), (0, 0, w, h)


def etiqueta_lockup(dark=False):
    fg = W if dark else K
    tg, (a, b, w, h) = etiqueta(tagfill=(R if False else (W if dark else K)), tagtext=(K if dark else W), hole_bg=(K if dark else W))
    word, ww, wb = tp(BOLD, 'MULTIREPUESTO', 112, w + 56, 0, tracking=0.035, fill=fg)
    cap = wb[3] - wb[1]
    y_base = h / 2 + cap / 2 - 14
    word, ww, wb = tp(BOLD, 'MULTIREPUESTO', 112, w + 56, y_base, tracking=0.035, fill=fg)
    bar = f'<rect x="{w + 56:.1f}" y="{y_base + 26:.1f}" width="64" height="7" fill="{R}"/>'
    desc, dw, db = tp(MONO, 'REPUESTOS Y AUTOPARTES', 20, w + 56 + 84, y_base + 36, tracking=0.12, fill=(('#B9BCC2') if dark else G))
    return tg + word + bar + desc, (0, 0, wb[2], h)


# ---------------------------------------------------------------- RUTA 3 · EJE
def monograma_eje(fg=K, accent=R, H=200, s=46):
    """E y M en bloque, separadas por un eje de simetría (línea de centros) en rojo."""
    ew, mw = H * 0.52, H * 0.80
    gap = H * 0.50
    def E(x0):
        return (f'<rect x="{x0}" y="0" width="{s}" height="{H}" fill="{fg}"/>'
                f'<rect x="{x0}" y="0" width="{ew}" height="{s}" fill="{fg}"/>'
                f'<rect x="{x0}" y="{(H - s) / 2}" width="{ew * 0.84}" height="{s}" fill="{fg}"/>'
                f'<rect x="{x0}" y="{H - s}" width="{ew}" height="{s}" fill="{fg}"/>')
    def M(x0):
        cx = x0 + mw / 2
        pts = f'{x0 + s / 2},{H + 20} {x0 + s / 2},0 {cx},{H * 0.64} {x0 + mw - s / 2},0 {x0 + mw - s / 2},{H + 20}'
        return (f'<clipPath id="mclip{int(x0)}"><rect x="{x0 - 5}" y="0" width="{mw + 10}" height="{H}"/></clipPath>'
                f'<polyline points="{pts}" fill="none" stroke="{fg}" stroke-width="{s}" stroke-linejoin="miter" '
                f'stroke-miterlimit="12" clip-path="url(#mclip{int(x0)})"/>')
    ax = ew + gap / 2
    total = ew + gap + mw
    axis = (f'<line x1="{ax}" y1="{-H * 0.16}" x2="{ax}" y2="{H * 1.16}" stroke="{accent}" stroke-width="{s * 0.16:.1f}" '
            f'stroke-dasharray="{s * 0.9:.1f} {s * 0.22:.1f} {s * 0.16:.1f} {s * 0.22:.1f}"/>')
    return E(0) + axis + M(ew + gap), (0, -H * 0.16, total, H * 1.16)


def eje_lockup(dark=False):
    fg = W if dark else K
    mono, (a, b, w, h) = monograma_eje(fg=fg)
    word, ww, wb = tp(BOLD, 'MULTIREPUESTO', 112, 0, 0, tracking=0.035, fill=fg)
    gx = w + 70
    cap = wb[3] - wb[1]
    base = (200 - cap) / 2 + cap
    word, ww, wb = tp(BOLD, 'MULTIREPUESTO', 112, gx, base - 38, tracking=0.035, fill=fg)
    desc, dw, db = tp(MONO, 'E&M · REPUESTOS Y AUTOPARTES', 20, gx, base + 20, tracking=0.12, fill=(('#B9BCC2') if dark else G))
    bar = f'<rect x="{gx:.1f}" y="{base - 12:.1f}" width="64" height="7" fill="{R}"/>'
    return mono + word + bar + desc, (0, -32, wb[2], 232)


# ---------------------------------------------------------------- HOJA
def panel(x, y, w, h, bg, inner, bounds, label, label_color, fill=0.74):
    bx0, by0, bx1, by1 = bounds
    bw, bh = bx1 - bx0, by1 - by0
    scale = min(w * fill / bw, (h - 110) / bh)
    cw, ch = bw * scale, bh * scale
    tx = x + (w - cw) / 2 - bx0 * scale
    ty = y + 40 + (h - 40 - ch) / 2 - by0 * scale
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>'
            f'<g transform="translate({tx:.1f},{ty:.1f}) scale({scale:.4f})">{inner}</g>'
            + tp(MONO, label, 16, x + 28, y + 40, tracking=0.12, fill=label_color)[0])


def hoja():
    Wd = 1600
    rows = []
    c_l, b1 = cota(K)
    c_d, _ = cota(W)
    rows.append(('RUTA 1 · COTA', c_l, c_d, b1))
    e_l, b2 = etiqueta_lockup(False)
    e_d, _ = etiqueta_lockup(True)
    rows.append(('RUTA 2 · ETIQUETA', e_l, e_d, b2))
    j_l, b3 = eje_lockup(False)
    j_d, _ = eje_lockup(True)
    rows.append(('RUTA 3 · EJE', j_l, j_d, b3))
    out = []
    y = 40
    for name, light, dark, b in rows:
        out.append(panel(40, y, 1000, 360, W, light, b, name, G))
        out.append(panel(1060, y, 500, 360, K, dark, b, 'NEGATIVO', '#9A9DA3', fill=0.86))
        y += 380
    H = y + 20
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{H}" viewBox="0 0 {Wd} {H}">'
            f'<rect width="{Wd}" height="{H}" fill="#D9DADD"/>' + ''.join(out) + '</svg>'), H


if __name__ == '__main__':
    svg, h = hoja()
    open(os.path.join(os.path.dirname(__file__), 'rutas.svg'), 'w').write(svg)
    print('ok', h)

import os, sys
from routes import tp, XB, BOLD, MONO, R, K, W, G

def cota_line(x0, x1, y, size, accent=R, label=None, label_fill=None, th=None):
    """Línea de cota entre x0 y x1; si hay label, se centra interrumpiendo la línea."""
    sw = max(size * 0.045, 2.5); al = size * 0.30; ah = size * 0.115
    th = th or size * 0.30
    g = [f'<line x1="{x0:.2f}" y1="{y - th:.2f}" x2="{x0:.2f}" y2="{y + th:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<line x1="{x1:.2f}" y1="{y - th:.2f}" x2="{x1:.2f}" y2="{y + th:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>',
         f'<polygon points="{x0 + sw/2:.2f},{y:.2f} {x0 + sw/2 + al:.2f},{y - ah:.2f} {x0 + sw/2 + al:.2f},{y + ah:.2f}" fill="{accent}"/>',
         f'<polygon points="{x1 - sw/2:.2f},{y:.2f} {x1 - sw/2 - al:.2f},{y - ah:.2f} {x1 - sw/2 - al:.2f},{y + ah:.2f}" fill="{accent}"/>']
    if label:
        lab, lw, lb = tp(XB, label, size, (x0 + x1) / 2, y + size * 0.36, tracking=0.03, anchor='middle', fill=label_fill or accent)
        gap = size * 0.22
        a, b = (x0 + x1) / 2 - lw / 2 - gap, (x0 + x1) / 2 + lw / 2 + gap
        g.append(f'<line x1="{x0 + al*0.9:.2f}" y1="{y:.2f}" x2="{a:.2f}" y2="{y:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>')
        g.append(f'<line x1="{b:.2f}" y1="{y:.2f}" x2="{x1 - al*0.9:.2f}" y2="{y:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>')
        g.append(lab)
    else:
        g.append(f'<line x1="{x0 + al*0.9:.2f}" y1="{y:.2f}" x2="{x1 - al*0.9:.2f}" y2="{y:.2f}" stroke="{accent}" stroke-width="{sw:.2f}"/>')
    return ''.join(g)

def avatar(bg, fg, accent, s=400):
    """Cuadrado: E&M grande con la cota debajo."""
    size = s * 0.42
    t, w, b = tp(XB, 'E&M', size, s / 2, 0, tracking=0.02, anchor='middle', fill=fg)
    cap = b[3] - b[1]
    base = s / 2 - cap / 2 + cap - s * 0.06
    t, w, b = tp(XB, 'E&M', size, s / 2, base, tracking=0.02, anchor='middle', fill=fg)
    ly = base + s * 0.17
    return (f'<rect width="{s}" height="{s}" fill="{bg}"/>' + t +
            cota_line(b[0], b[2], ly, s * 0.13, accent), s)

def strip(fg, accent, size=100, width=520):
    """Versión horizontal para pecho / sellos: |◄— E&M —►|."""
    return cota_line(0, width, 0, size * 0.62, accent, label='E&M', label_fill=fg, th=size * 0.28)

def sheet():
    out = ['<rect width="1600" height="1000" fill="#D9DADD"/>']
    # fila 1: avatares
    items = [(K, W, R), (R, W, K), (W, K, R), ('#EDEDEE', K, R)]
    for i, (bg, fg, ac) in enumerate(items):
        body, s = avatar(bg, fg, ac, 340)
        out.append(f'<g transform="translate({40 + i * 385},40)">{body}</g>')
    out.append(tp(MONO, 'SÍMBOLO COMPACTO · PERFIL, SELLO, ETIQUETA', 15, 40, 420, tracking=0.12, fill=G)[0])
    # fila 2: tiras
    out.append(f'<rect x="40" y="450" width="760" height="230" fill="{K}"/>')
    out.append(f'<g transform="translate(140,565)">{strip(W, R, 100, 560)}</g>')
    out.append(f'<rect x="820" y="450" width="740" height="230" fill="{W}"/>')
    out.append(f'<g transform="translate(920,565)">{strip(K, R, 100, 540)}</g>')
    out.append(tp(MONO, 'VERSIÓN HORIZONTAL · BORDADO EN PECHO (8 CM), CINTA, EMBALAJE', 15, 40, 710, tracking=0.12, fill=G)[0])
    # fila 3: sistema gráfico
    out.append(f'<rect x="40" y="740" width="1520" height="220" fill="{W}"/>')
    x = 80
    for lab, wv, tag in [('Pastillas de freno', 168, 'REF. 0412'), ('Filtro de aceite', 132, 'REF. 0087'), ('Bomba de agua', 214, 'REF. 0230')]:
        t, tw, tb = tp(XB, lab.upper(), 34, x, 830, tracking=0.02, fill=K)
        out.append(t)
        out.append(cota_line(tb[0], tb[2], 878, 26, R, label=str(wv) + ' mm', label_fill=R))
        out.append(tp(MONO, tag, 15, x, 935, tracking=0.12, fill=G)[0])
        x += 500
    out.append(tp(MONO, 'SISTEMA GRÁFICO · CADA PIEZA LLEVA SU MEDIDA Y SU REFERENCIA', 15, 80, 775, tracking=0.12, fill=G)[0])
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">' + ''.join(out) + '</svg>'

if __name__ == '__main__':
    open(os.path.join(os.path.dirname(__file__), 'cota_sistema.svg'), 'w').write(sheet())
    print('ok')

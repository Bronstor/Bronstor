"""Mockup del polo (frente y espalda), dibujado en un lienzo de 1000 x 1100."""
from common import sym, logo_v, R

BODY = ('M 390 95 C 340 110 280 125 225 150 C 170 175 120 270 88 395 L 212 448 '
        'C 230 430 245 415 258 398 C 262 600 250 850 248 1040 Q 500 1064 752 1040 '
        'C 750 850 738 600 742 398 C 755 415 770 430 788 448 L 912 395 '
        'C 880 270 830 175 775 150 C 720 125 660 110 610 95 {neck} Z')
NECK_FRONT = 'C 560 130 440 130 390 95'
NECK_BACK = 'C 560 112 440 112 390 95'


def polo(uid, front=True, base='#1A1A1B', tip=R):
    body = BODY.format(neck=NECK_FRONT if front else NECK_BACK)
    g = []
    g.append(f'<defs><clipPath id="c{uid}"><path d="{body}"/></clipPath>'
             f'<linearGradient id="g{uid}" x1="0" x2="1" y1="0" y2="0">'
             f'<stop offset="0" stop-color="#000" stop-opacity="0.55"/>'
             f'<stop offset="0.24" stop-color="#000" stop-opacity="0.05"/>'
             f'<stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/>'
             f'<stop offset="0.76" stop-color="#000" stop-opacity="0.05"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0.55"/></linearGradient>'
             f'<linearGradient id="v{uid}" x1="0" x2="0" y1="0" y2="1">'
             f'<stop offset="0" stop-color="#fff" stop-opacity="0.07"/>'
             f'<stop offset="0.5" stop-color="#fff" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0.25"/></linearGradient></defs>')
    # sombra en el piso
    g.append('<ellipse cx="500" cy="1078" rx="330" ry="26" fill="#000" opacity="0.32" filter="url(#floor)"/>')
    g.append(f'<path d="{body}" fill="{base}"/>')
    sh = [f'<rect width="1000" height="1100" fill="url(#g{uid})"/>',
          f'<rect width="1000" height="1100" fill="url(#v{uid})"/>',
          # pliegues
          '<path d="M 262 420 C 330 470 360 520 380 600" stroke="#000" stroke-opacity="0.55" stroke-width="22" fill="none" filter="url(#soft)"/>',
          '<path d="M 738 420 C 670 470 640 520 620 600" stroke="#000" stroke-opacity="0.55" stroke-width="22" fill="none" filter="url(#soft)"/>',
          '<path d="M 285 440 C 340 480 365 520 385 575" stroke="#fff" stroke-opacity="0.07" stroke-width="16" fill="none" filter="url(#soft)"/>',
          '<path d="M 300 860 C 420 900 580 900 700 860" stroke="#000" stroke-opacity="0.25" stroke-width="26" fill="none" filter="url(#soft)"/>',
          '<path d="M 300 820 C 420 860 580 860 700 820" stroke="#fff" stroke-opacity="0.06" stroke-width="18" fill="none" filter="url(#soft)"/>',
          '<path d="M 330 700 C 380 720 420 760 430 820" stroke="#000" stroke-opacity="0.35" stroke-width="16" fill="none" filter="url(#soft)"/>',
          '<path d="M 690 690 C 640 720 600 770 590 830" stroke="#000" stroke-opacity="0.3" stroke-width="16" fill="none" filter="url(#soft)"/>',
          '<path d="M 140 300 C 170 330 200 360 215 420" stroke="#fff" stroke-opacity="0.07" stroke-width="22" fill="none" filter="url(#soft)"/>',
          '<path d="M 860 300 C 830 330 800 360 785 420" stroke="#000" stroke-opacity="0.35" stroke-width="22" fill="none" filter="url(#soft)"/>',
          # textura piqué
          '<rect width="1000" height="1100" filter="url(#fabric)"/>',
          '<rect width="1000" height="1100" filter="url(#fabricDark)"/>']
    # costuras: hombro/sisa
    seams = ['M 225 150 C 250 230 264 330 258 398', 'M 775 150 C 750 230 736 330 742 398']
    for s in seams:
        sh.append(f'<path d="{s}" stroke="#000" stroke-opacity="0.6" stroke-width="3" fill="none"/>')
        sh.append(f'<path d="{s}" stroke="#fff" stroke-opacity="0.16" stroke-width="1.6" stroke-dasharray="5 4" fill="none" transform="translate(7,0)"/>')
    # dobladillo
    sh.append('<path d="M 249 1012 Q 500 1036 751 1012" stroke="#fff" stroke-opacity="0.16" stroke-width="1.6" stroke-dasharray="5 4" fill="none"/>')
    sh.append('<path d="M 249 1020 Q 500 1044 751 1020" stroke="#000" stroke-opacity="0.4" stroke-width="2" fill="none"/>')
    # puños acanalados con ribete rojo
    for (a, b, c, d) in [((88, 395), (212, 448), (223, 418), (99, 365)), ((912, 395), (788, 448), (777, 418), (901, 365))]:
        sh.append(f'<polygon points="{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]} {d[0]},{d[1]}" fill="#000" opacity="0.25"/>')
        for t in [0.2, 0.32, 0.44, 0.56, 0.68, 0.8]:
            x1 = a[0] + (b[0] - a[0]) * t; y1 = a[1] + (b[1] - a[1]) * t
            x2 = d[0] + (c[0] - d[0]) * t; y2 = d[1] + (c[1] - d[1]) * t
            sh.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-opacity="0.35" stroke-width="2"/>')
        mx1 = a[0] + (d[0] - a[0]) * 0.42; my1 = a[1] + (d[1] - a[1]) * 0.42
        mx2 = b[0] + (c[0] - b[0]) * 0.42; my2 = b[1] + (c[1] - b[1]) * 0.42
        sh.append(f'<line x1="{mx1:.1f}" y1="{my1:.1f}" x2="{mx2:.1f}" y2="{my2:.1f}" stroke="{tip}" stroke-width="6"/>')
        sh.append(f'<line x1="{d[0]}" y1="{d[1]}" x2="{c[0]}" y2="{c[1]}" stroke="#000" stroke-opacity="0.5" stroke-width="2.5"/>')
    if front:
        # interior del cuello (espalda vista por dentro)
        sh.append('<path d="M 392 96 C 430 58 570 58 608 96 C 570 82 430 82 392 96 Z" fill="#0A0A0A"/>')
        # tapeta con botones
        sh.append(f'<rect x="474" y="128" width="52" height="250" fill="{base}"/>')
        sh.append('<rect x="474" y="128" width="52" height="250" fill="#000" opacity="0.12"/>')
        sh.append('<rect x="474" y="128" width="52" height="250" fill="none" stroke="#000" stroke-opacity="0.6" stroke-width="2.5"/>')
        sh.append('<rect x="481" y="135" width="38" height="236" fill="none" stroke="#fff" stroke-opacity="0.15" stroke-width="1.4" stroke-dasharray="5 4"/>')
        sh.append('<path d="M 474 378 L 526 378" stroke="#fff" stroke-opacity="0.15" stroke-width="1.4" stroke-dasharray="5 4"/>')
        for by in [240, 318]:
            sh.append(f'<circle cx="500" cy="{by}" r="10" fill="#0E0E0E" stroke="#3A3A3A" stroke-width="1.5"/>'
                      f'<circle cx="496" cy="{by}" r="1.8" fill="#444"/><circle cx="504" cy="{by}" r="1.8" fill="#444"/>')
        g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
        # cuello: solapas con ribete rojo
        for flip in [False, True]:
            tr = 'transform="translate(1000,0) scale(-1,1)"' if flip else ''
            flap = 'M 392 88 C 382 140 398 192 424 226 L 500 178 C 474 152 456 122 452 100 C 432 98 410 94 392 88 Z'
            g.append(f'<g {tr}><path d="{flap}" fill="{base}"/>'
                     f'<path d="{flap}" fill="#000" opacity="0.18"/>'
                     f'<path d="M 395 92 C 386 140 401 190 425 221 L 494 176" stroke="{tip}" stroke-width="5" fill="none"/>'
                     f'<path d="M 404 98 C 396 140 410 184 430 210 L 482 176" stroke="#fff" stroke-opacity="0.15" stroke-width="1.3" stroke-dasharray="4 4" fill="none"/>'
                     f'<path d="{flap}" fill="none" stroke="#000" stroke-opacity="0.7" stroke-width="2"/>'
                     f'<path d="M 424 226 L 500 178" stroke="#000" stroke-opacity="0.5" stroke-width="10" filter="url(#soft6)" transform="translate(0,10)"/></g>')
        # símbolo bordado en el pecho izquierdo (derecha del espectador)
        g.append(f'<g filter="url(#emb)">{sym(648, 300, 118)}</g>')
    else:
        g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
        # cuello por detrás con ribete
        g.append(f'<path d="M 388 96 C 430 116 570 116 612 96 L 616 58 C 570 40 430 40 384 58 Z" fill="{base}"/>'
                 f'<path d="M 388 96 C 430 116 570 116 612 96 L 616 58 C 570 40 430 40 384 58 Z" fill="#000" opacity="0.2"/>'
                 f'<path d="M 386 62 C 430 44 570 44 614 62" stroke="{tip}" stroke-width="5" fill="none"/>'
                 f'<path d="M 388 96 C 430 116 570 116 612 96" stroke="#000" stroke-opacity="0.7" stroke-width="2.5" fill="none"/>')
        lg, h = logo_v(500, 210, 340)
        g.append(f'<g filter="url(#print)" opacity="0.96">{lg}</g>')
    return ''.join(g)

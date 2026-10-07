"""Camisa de trabajo, casaca y gorra."""
from common import sym, logo_h, logo_v, text, R, K, W

LONG = ('M 400 90 C 340 105 285 120 235 145 C 185 170 160 230 150 330 L 105 960 L 225 975 '
        'L 262 470 C 264 650 258 870 256 1060 Q 500 1085 744 1060 C 742 870 736 650 738 470 '
        'L 775 975 L 895 960 L 850 330 C 840 230 815 170 765 145 C 715 120 660 105 600 90 {neck} Z')
NECK_F = 'C 560 125 440 125 400 90'
NECK_B = 'C 560 108 440 108 400 90'
ARM_L = 'M 235 145 C 255 250 268 380 262 470'
ARM_R = 'M 765 145 C 745 250 732 380 738 470'


def stitch(d, op=0.16, w=1.5, extra=''):
    return f'<path d="{d}" stroke="#fff" stroke-opacity="{op}" stroke-width="{w}" stroke-dasharray="5 4" fill="none" {extra}/>'


def seam(d, op=0.6, w=2.5, extra=''):
    return f'<path d="{d}" stroke="#000" stroke-opacity="{op}" stroke-width="{w}" fill="none" {extra}/>'


def shading(uid):
    return (f'<defs><linearGradient id="g{uid}" x1="0" x2="1">'
            '<stop offset="0" stop-color="#000" stop-opacity="0.55"/><stop offset="0.25" stop-color="#000" stop-opacity="0.04"/>'
            '<stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/><stop offset="0.75" stop-color="#000" stop-opacity="0.04"/>'
            '<stop offset="1" stop-color="#000" stop-opacity="0.55"/></linearGradient>'
            f'<linearGradient id="v{uid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.06"/>'
            '<stop offset="0.5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.28"/></linearGradient></defs>')


def folds_long():
    f = []
    for d, c, o, w in [
        ('M 266 480 C 330 520 360 580 372 660', '#000', 0.5, 22), ('M 734 480 C 670 520 640 580 628 660', '#000', 0.5, 22),
        ('M 300 900 C 420 930 580 930 700 900', '#000', 0.25, 24), ('M 300 860 C 420 890 580 890 700 860', '#fff', 0.05, 16),
        ('M 170 420 C 175 520 160 640 150 760', '#fff', 0.07, 26), ('M 830 420 C 825 520 840 640 850 760', '#000', 0.4, 26),
        ('M 200 560 C 215 600 220 640 210 700', '#000', 0.4, 14), ('M 800 560 C 785 600 780 640 790 700', '#000', 0.4, 14),
        ('M 130 820 C 160 830 200 840 230 835', '#000', 0.35, 12), ('M 870 820 C 840 830 800 840 770 835', '#000', 0.35, 12),
        ('M 340 720 C 380 740 410 780 420 840', '#000', 0.3, 16), ('M 660 720 C 620 740 590 780 580 840', '#000', 0.3, 16)]:
        f.append(f'<path d="{d}" stroke="{c}" stroke-opacity="{o}" stroke-width="{w}" fill="none" filter="url(#soft)"/>')
    return ''.join(f)


def cuffs(base, tip=None):
    out = []
    for flip in [False, True]:
        tr = 'transform="translate(1000,0) scale(-1,1)"' if flip else ''
        cuff = 'M 108 922 L 228 936 L 225 975 L 105 960 Z'
        out.append(f'<g {tr}><path d="{cuff}" fill="{base}"/><path d="{cuff}" fill="#000" opacity="0.22"/>'
                   + seam('M 108 922 L 228 936') + stitch('M 108 930 L 227 944') + stitch('M 106 952 L 225 967'))
        if tip:
            out.append(f'<path d="M 107 938 L 227 952" stroke="{tip}" stroke-width="5"/>')
        out.append('<circle cx="205" cy="950" r="6" fill="#0E0E0E" stroke="#444" stroke-width="1.2"/></g>')
    return ''.join(out)


def shirt(uid, front=True, base='#2B2D31', yoke='#141414'):
    body = LONG.format(neck=NECK_F if front else NECK_B)
    g = [shading(uid), f'<defs><clipPath id="c{uid}"><path d="{body}"/></clipPath></defs>',
         '<ellipse cx="500" cy="1090" rx="360" ry="26" fill="#000" opacity="0.32" filter="url(#floor)"/>',
         f'<path d="{body}" fill="{base}"/>']
    sh = []
    yk = ('M 400 90 C 340 105 285 120 235 145 C 243 175 249 205 253 235 Q 500 250 747 235 '
          'C 751 205 757 175 765 145 C 715 120 660 105 600 90 Z')
    sh.append(f'<path d="{yk}" fill="{yoke}"/>')
    sh.append(f'<path d="M 253 235 Q 500 250 747 235" stroke="{R}" stroke-width="6" fill="none"/>')
    sh.append(stitch('M 254 246 Q 500 261 746 246'))
    sh.append(f'<rect width="1000" height="1150" fill="url(#g{uid})"/><rect width="1000" height="1150" fill="url(#v{uid})"/>')
    sh.append(folds_long())
    sh.append('<rect width="1000" height="1150" filter="url(#fabric)"/><rect width="1000" height="1150" filter="url(#fabricDark)"/>')
    for a in [ARM_L, ARM_R]:
        sh.append(seam(a, 0.65, 3) + stitch(a, extra='transform="translate(6,0)"'))
    sh.append(seam('M 262 470 L 225 975', 0.5, 2) + seam('M 738 470 L 775 975', 0.5, 2))
    sh.append(stitch('M 257 1034 Q 500 1058 743 1034') + seam('M 257 1042 Q 500 1066 743 1042', 0.4, 2))
    if front:
        sh.append('<path d="M 400 92 C 440 60 560 60 600 92 C 560 80 440 80 400 92 Z" fill="#0A0A0A"/>')
        sh.append(f'<rect x="472" y="118" width="56" height="955" fill="{base}"/><rect x="472" y="118" width="56" height="955" fill="#000" opacity="0.1"/>')
        sh.append(seam('M 472 118 L 472 1073') + seam('M 528 118 L 528 1073'))
        sh.append(stitch('M 480 130 L 480 1068') + stitch('M 520 130 L 520 1068'))
        for by in range(300, 1000, 140):
            sh.append(f'<circle cx="500" cy="{by}" r="11" fill="#111" stroke="#4A4A4A" stroke-width="1.5"/>'
                      f'<circle cx="496" cy="{by}" r="1.8" fill="#555"/><circle cx="504" cy="{by}" r="1.8" fill="#555"/>')
        for x0 in [298, 562]:
            sh.append(f'<path d="M {x0} 300 h 140 v 170 l -70 18 l -70 -18 Z" fill="{base}"/>'
                      f'<path d="M {x0} 300 h 140 v 170 l -70 18 l -70 -18 Z" fill="#000" opacity="0.08"/>'
                      + seam(f'M {x0} 300 v 170 l 70 18 l 70 -18 v -170', 0.55, 2.2)
                      + stitch(f'M {x0 + 7} 306 v 160 l 63 16 l 63 -16 v -160')
                      + f'<path d="M {x0 - 4} 286 h 148 v 46 l -74 12 l -74 -12 Z" fill="{base}"/>'
                      + f'<path d="M {x0 - 4} 286 h 148 v 46 l -74 12 l -74 -12 Z" fill="#000" opacity="0.15"/>'
                      + seam(f'M {x0 - 4} 286 h 148 v 46 l -74 12 l -74 -12 Z', 0.6, 2.2)
                      + stitch(f'M {x0 + 3} 292 h 134 v 36 l -67 11 l -67 -11 Z')
                      + f'<path d="M {x0 - 4} 344 l 74 12 l 74 -12" stroke="#000" stroke-opacity="0.5" stroke-width="10" fill="none" filter="url(#soft6)"/>'
                      + f'<circle cx="{x0 + 70}" cy="330" r="7" fill="#111" stroke="#4A4A4A" stroke-width="1.2"/>')
        sh.append(cuffs(base))
        g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
        # cuello camisero
        for flip in [False, True]:
            tr = 'transform="translate(1000,0) scale(-1,1)"' if flip else ''
            flap = 'M 400 84 C 388 130 392 180 404 226 L 500 160 C 480 140 464 116 458 96 C 438 94 420 90 400 84 Z'
            g.append(f'<g {tr}><path d="{flap}" fill="{yoke}"/>' + stitch('M 408 96 C 398 136 401 178 410 212 L 484 160')
                     + seam(flap, 0.8, 2) + '<path d="M 404 226 L 500 160" stroke="#000" stroke-opacity="0.5" stroke-width="10" filter="url(#soft6)" transform="translate(0,10)"/></g>')
        # parche con nombre (izq. del espectador) y símbolo bordado (der.)
        g.append(f'<g filter="url(#emb)"><rect x="300" y="370" width="136" height="44" rx="6" fill="#111" stroke="{R}" stroke-width="3"/>'
                 + text('[NOMBRE]', 368, 399, 17, 'ArchivoExpBlack.ttf', W, anchor='middle', skew=0.21) + '</g>')
        g.append(f'<g filter="url(#emb)">{sym(632, 410, 104)}</g>')
    else:
        sh.append(cuffs(base))
        g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
        g.append(f'<path d="M 398 92 C 440 112 560 112 602 92 L 606 58 C 560 42 440 42 394 58 Z" fill="{yoke}"/>'
                 + seam('M 398 92 C 440 112 560 112 602 92 L 606 58 C 560 42 440 42 394 58 Z', 0.8, 2)
                 + stitch('M 400 66 C 440 52 560 52 600 66'))
        lg, h = logo_h(292, 330, 416)
        g.append(f'<g filter="url(#print)" opacity="0.96">{lg}</g>')
    return ''.join(g)


def jacket(uid, base='#141415', panel='#2B2D31'):
    """Casaca softshell negra con paneles laterales grises y cierre rojo."""
    body = LONG.format(neck='C 560 100 440 100 400 90')
    g = [shading(uid), f'<defs><clipPath id="c{uid}"><path d="{body}"/></clipPath></defs>',
         '<ellipse cx="500" cy="1090" rx="360" ry="26" fill="#000" opacity="0.35" filter="url(#floor)"/>',
         f'<path d="{body}" fill="{base}"/>']
    sh = []
    # paneles laterales grises
    sh.append(f'<path d="M 150 330 C 160 230 185 170 235 145 C 255 250 268 380 262 470 L 225 975 L 105 960 Z" fill="{panel}" opacity="0.0"/>')
    sh.append(f'<path d="M 262 470 C 264 650 258 870 256 1060 L 330 1068 C 326 860 318 640 300 470 Z" fill="{panel}"/>')
    sh.append(f'<path d="M 738 470 C 736 650 742 870 744 1060 L 670 1068 C 674 860 682 640 700 470 Z" fill="{panel}"/>')
    sh.append(seam('M 300 470 C 318 640 326 860 330 1068', 0.7, 2.5) + seam('M 700 470 C 682 640 674 860 670 1068', 0.7, 2.5))
    sh.append(f'<rect width="1000" height="1150" fill="url(#g{uid})"/><rect width="1000" height="1150" fill="url(#v{uid})"/>')
    sh.append(folds_long())
    sh.append('<rect width="1000" height="1150" filter="url(#fabricDark)"/>')
    for a in [ARM_L, ARM_R]:
        sh.append(seam(a, 0.7, 3) + stitch(a, 0.12, extra='transform="translate(6,0)"'))
    # cierre central
    sh.append('<rect x="494" y="60" width="12" height="1010" fill="#0A0A0A"/>')
    sh.append(f'<line x1="500" y1="62" x2="500" y2="1068" stroke="{R}" stroke-width="3.5" stroke-dasharray="3 2"/>')
    # bolsillos con cierre en diagonal
    sh.append(f'<path d="M 330 640 L 380 520" stroke="#0A0A0A" stroke-width="9"/><path d="M 330 640 L 380 520" stroke="{R}" stroke-width="2.5" stroke-dasharray="2 2"/>')
    sh.append(f'<path d="M 670 640 L 620 520" stroke="#0A0A0A" stroke-width="9"/><path d="M 670 640 L 620 520" stroke="{R}" stroke-width="2.5" stroke-dasharray="2 2"/>')
    # pretina inferior
    sh.append(f'<path d="M 256 1020 Q 500 1044 744 1020 L 744 1060 Q 500 1085 256 1060 Z" fill="#000" opacity="0.3"/>')
    sh.append(stitch('M 257 1028 Q 500 1052 743 1028', 0.12))
    sh.append(cuffs('#0E0E0F', tip=None))
    g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
    # cuello alto
    g.append(f'<path d="M 400 92 C 440 104 560 104 600 92 L 606 30 C 560 18 440 18 394 30 Z" fill="{base}"/>'
             '<path d="M 400 92 C 440 104 560 104 600 92 L 606 30 C 560 18 440 18 394 30 Z" fill="#fff" opacity="0.04"/>'
             + seam('M 400 92 C 440 104 560 104 600 92 L 606 30 C 560 18 440 18 394 30 Z', 0.8, 2)
             + f'<path d="M 396 36 C 440 25 560 25 604 36" stroke="{R}" stroke-width="4" fill="none"/>'
             + '<rect x="494" y="24" width="12" height="80" fill="#0A0A0A"/>'
             + f'<rect x="489" y="96" width="22" height="40" rx="5" fill="{R}"/><rect x="496" y="104" width="8" height="18" rx="3" fill="#7A0A0E"/>')
    g.append(f'<g filter="url(#emb)">{sym(640, 270, 112)}</g>')
    return ''.join(g)


def cap(uid, base='#151516'):
    crown = 'M 180 560 C 175 330 300 180 500 175 C 700 180 825 330 820 560 C 700 612 300 612 180 560 Z'
    visor = 'M 172 552 C 300 606 700 606 828 552 C 868 560 878 585 860 612 C 760 712 240 712 140 612 C 122 585 132 560 172 552 Z'
    g = [f'<defs><clipPath id="c{uid}"><path d="{crown}"/></clipPath>'
         f'<radialGradient id="r{uid}" cx="50%" cy="25%" r="80%"><stop offset="0" stop-color="#fff" stop-opacity="0.12"/>'
         '<stop offset="0.6" stop-color="#000" stop-opacity="0.05"/><stop offset="1" stop-color="#000" stop-opacity="0.6"/></radialGradient>'
         f'<linearGradient id="vz{uid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0C0C0D"/><stop offset="0.45" stop-color="#232325"/><stop offset="1" stop-color="#121213"/></linearGradient>'
         '</defs>',
         '<ellipse cx="500" cy="730" rx="380" ry="34" fill="#000" opacity="0.35" filter="url(#floor)"/>',
         f'<path d="{crown}" fill="{base}"/>']
    sh = [f'<rect width="1000" height="800" fill="url(#r{uid})"/>',
          '<rect width="1000" height="800" filter="url(#fabric)"/><rect width="1000" height="800" filter="url(#fabricDark)"/>',
          seam('M 500 178 C 360 220 300 380 300 590', 0.7, 3) + stitch('M 490 182 C 356 226 296 380 292 588', 0.14)
          + stitch('M 510 182 C 370 226 312 380 308 592', 0.14),
          seam('M 500 178 C 640 220 700 380 700 590', 0.7, 3) + stitch('M 490 182 C 630 226 688 380 692 592', 0.14)
          + stitch('M 510 182 C 644 226 704 380 708 588', 0.14),
          seam('M 500 178 L 500 600', 0.5, 2.5),
          '<path d="M 260 470 C 280 420 300 400 330 380" stroke="#fff" stroke-opacity="0.06" stroke-width="30" fill="none" filter="url(#soft)"/>',
          '<circle cx="300" cy="330" r="9" fill="#0A0A0A" stroke="#333" stroke-width="2"/>',
          '<circle cx="700" cy="330" r="9" fill="#0A0A0A" stroke="#333" stroke-width="2"/>']
    g.append(f'<g clip-path="url(#c{uid})">{"".join(sh)}</g>')
    g.append('<ellipse cx="500" cy="178" rx="26" ry="11" fill="#1E1E20" stroke="#000" stroke-width="2"/>')
    g.append(f'<g filter="url(#emb)">{sym(500, 390, 250)}</g>')
    # visera
    g.append(f'<path d="{visor}" fill="url(#vz{uid})"/>'
             '<path d="M 180 562 C 300 614 700 614 820 562" stroke="#000" stroke-opacity="0.7" stroke-width="18" fill="none" filter="url(#soft6)" transform="translate(0,8)"/>'
             + stitch('M 160 590 C 280 670 720 670 840 590', 0.18) + stitch('M 152 602 C 270 688 730 688 848 602', 0.18)
             + f'<path d="M 142 614 C 240 714 760 714 858 614" stroke="{R}" stroke-width="6" fill="none"/>'
             + seam(visor, 0.8, 2) + seam('M 180 560 C 300 612 700 612 820 560', 0.8, 2.5))
    return ''.join(g)

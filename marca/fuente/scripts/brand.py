"""Láminas de portada, sistema de logo y colores/tipografía."""
from common import sym, logo_h, logo_v, text, scene, save, caption, R, K, W


def board_portada():
    W_, H_ = 1600, 1000
    lg, h = logo_v(800, 0, 620)
    b = [f'<g transform="translate(0,{(H_ - h) / 2 - 40:.1f})">{lg}</g>',
         text('MANUAL DE IDENTIDAD VISUAL', 800, 900, 15, 'PlexMono.ttf', '#9A9DA3', anchor='middle', tracking=0.3),
         f'<rect x="770" y="860" width="60" height="5" fill="{R}"/>']
    return save('00-portada', scene(W_, H_, ''.join(b), dark=True))


def board_logo():
    W_, H_ = 1600, 1000
    b = []
    # panel blanco grande
    b.append('<rect x="60" y="60" width="900" height="500" rx="8" fill="#FFFFFF"/>')
    lg, h = logo_h(140, 0, 740, dark=False)
    b.append(f'<g transform="translate(0,{310 - h / 2:.1f})">{lg}</g>')
    b.append(text('LOGO PRINCIPAL', 90, 100, 13, 'PlexMono.ttf', '#5F636A', tracking=0.15))
    # panel negro
    b.append(f'<rect x="990" y="60" width="550" height="500" rx="8" fill="{K}"/>')
    lg, h = logo_v(1265, 0, 380, dark=True)
    b.append(f'<g transform="translate(0,{318 - h / 2:.1f})">{lg}</g>')
    b.append(text('VERTICAL · NEGATIVO', 1020, 100, 13, 'PlexMono.ttf', '#9A9DA3', tracking=0.15))
    # fila de símbolos
    tiles = [('#FFFFFF', 'principal', 'SÍMBOLO', '#5F636A'), (R, 'negro', 'SOBRE ROJO', '#FFFFFF'),
             ('#EDEDEE', 'rojo', 'UNA TINTA ROJA', '#5F636A'), (K, 'rojo', 'BORDADO SIMPLE', '#9A9DA3')]
    for i, (bg, v, lab, lc) in enumerate(tiles):
        x = 60 + i * 375
        b.append(f'<rect x="{x}" y="590" width="355" height="250" rx="8" fill="{bg}"/>')
        b.append(sym(x + 177, 720, 170, v))
        b.append(text(lab, x + 24, 622, 12, 'PlexMono.ttf', lc, tracking=0.15))
    b.append(caption(W_, H_, 'Sistema de logo', 'Tuerca hexagonal + iniciales inclinadas 12° · mínimo 12 mm impreso / 48 px en pantalla'))
    return save('07-logo', scene(W_, H_, ''.join(b)))


def board_colores():
    W_, H_ = 1600, 1000
    cols = [('Negro Carbón', '#111111', '17 17 17', 'Black 6 C', W), ('Rojo E&M', '#D7141A', '215 20 26', '485 C', W),
            ('Rojo Profundo', '#9E0F14', '158 15 20', '7621 C', W), ('Gris Acero', '#5F636A', '95 99 106', 'Cool Gray 10 C', W),
            ('Gris Niebla', '#EDEDEE', '237 237 238', 'Cool Gray 1 C', K)]
    b = []
    widths = [460, 320, 240, 220, 240]
    x = 60
    for (n, hx, rgb, pms, tc), w in zip(cols, widths):
        b.append(f'<rect x="{x}" y="60" width="{w}" height="420" fill="{hx}"/>')
        b.append(text(n.upper(), x + 22, 400, 17, 'ArchivoExpBlack.ttf', tc, skew=0.21))
        b.append(text(hx, x + 22, 428, 13, 'PlexMono.ttf', tc))
        b.append(text('RGB ' + rgb, x + 22, 448, 13, 'PlexMono.ttf', tc))
        b.append(text('PMS ' + pms, x + 22, 468, 13, 'PlexMono.ttf', tc))
        x += w
    b.append('<rect x="60" y="60" width="1480" height="420" fill="none" stroke="#000" stroke-opacity="0.08"/>')
    # tipografía
    b.append(text('TÍTULOS · ARCHIVO EXPANDED BLACK, INCLINADA', 60, 560, 13, 'PlexMono.ttf', '#5F636A', tracking=0.12))
    b.append(text('FRENOS · FILTROS · SUSPENSIÓN', 60, 640, 58, 'ArchivoExpBlack.ttf', K, skew=0.21))
    b.append(text('TEXTOS · ARCHIVO REGULAR', 60, 720, 13, 'PlexMono.ttf', '#5F636A', tracking=0.12))
    b.append(text('Te ayudamos a encontrar la pieza exacta para tu vehículo.', 60, 764, 30, 'ArchivoRegular.ttf', K))
    b.append(text('CÓDIGOS Y PRECIOS · IBM PLEX MONO', 900, 720, 13, 'PlexMono.ttf', '#5F636A', tracking=0.12))
    b.append(text('REF. [CÓDIGO]   [PRECIO]', 900, 764, 30, 'PlexMono.ttf', R))
    b.append(text('Fuentes gratuitas (Google Fonts) · Proporción de uso: 60% negro · 30% blanco/gris · 10% rojo', 60, 820, 16, 'ArchivoRegular.ttf', '#5F636A'))
    b.append(caption(W_, H_, 'Colores y tipografía', 'Negro y rojo: fuerza, precisión y confianza'))
    return save('08-colores', scene(W_, H_, ''.join(b)))

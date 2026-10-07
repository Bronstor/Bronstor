"""Aplicaciones: fachada con letrero, tarjetas de presentación, plantilla de redes."""
from common import sym, logo_h, logo_v, text, scene, save, caption, R, K, W


def board_letrero():
    W_, H_ = 1600, 1000
    b = ['<defs>'
         '<linearGradient id="wall" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#26272B"/><stop offset="1" stop-color="#1A1B1E"/></linearGradient>'
         '<linearGradient id="glass" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#3A4450"/><stop offset="0.5" stop-color="#1B2129"/><stop offset="1" stop-color="#0F1318"/></linearGradient>'
         '<linearGradient id="walk" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#8E8F93"/><stop offset="1" stop-color="#5E6064"/></linearGradient>'
         '<linearGradient id="box" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1A1A1C"/><stop offset="1" stop-color="#0B0B0C"/></linearGradient>'
         '<radialGradient id="cone" cx="50%" cy="0%" r="100%"><stop offset="0" stop-color="#FFF6E0" stop-opacity="0.35"/><stop offset="1" stop-color="#FFF6E0" stop-opacity="0"/></radialGradient>'
         '<filter id="glow" filterUnits="userSpaceOnUse" x="-500" y="-500" width="3000" height="2000"><feGaussianBlur stdDeviation="18"/></filter>'
         '<filter id="concrete" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="3" seed="3"/>'
         '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.07 0"/></filter>'
         '</defs>']
    b.append('<rect width="1600" height="1000" fill="url(#wall)"/><rect width="1600" height="1000" filter="url(#concrete)"/>')
    # líneas de bloques en la pared
    for y in range(60, 860, 80):
        b.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="#000" stroke-opacity="0.18" stroke-width="2"/>')
    # vereda
    b.append('<rect x="0" y="880" width="1600" height="120" fill="url(#walk)"/><rect x="0" y="880" width="1600" height="120" filter="url(#concrete)"/>')
    b.append('<rect x="0" y="876" width="1600" height="8" fill="#3B3C40"/>')
    # luz ambiente del letrero sobre la pared
    b.append('<ellipse cx="800" cy="250" rx="760" ry="200" fill="#ffffff" opacity="0.06" filter="url(#glow)"/>')
    # caja de luz
    b.append('<rect x="170" y="110" width="1260" height="250" rx="6" fill="#000" opacity="0.5" filter="url(#soft)" transform="translate(0,18)"/>')
    b.append('<rect x="170" y="110" width="1260" height="250" rx="6" fill="url(#box)"/>')
    b.append('<rect x="170" y="110" width="1260" height="250" rx="6" fill="none" stroke="#2E2F33" stroke-width="3"/>')
    b.append(f'<rect x="170" y="338" width="1260" height="22" fill="{R}"/>')
    b.append('<rect x="170" y="110" width="1260" height="10" fill="#fff" opacity="0.05"/>')
    lg, h = logo_h(0, 0, 940)
    b.append(f'<g transform="translate(330,{110 + (228 - h) / 2:.1f})"><g filter="url(#glow)" opacity="0.55">{lg}</g>{lg}</g>')
    # vitrina
    b.append('<rect x="170" y="430" width="1260" height="450" fill="#2B2D31"/>')
    for x0, w in [(190, 380), (590, 420), (1030, 380)]:
        b.append(f'<rect x="{x0}" y="450" width="{w}" height="410" fill="url(#glass)"/>')
        b.append(f'<path d="M {x0 + 30} 450 L {x0 + 130} 450 L {x0 + 20} 860 L {x0} 860 L {x0} 560 Z" fill="#fff" opacity="0.05"/>')
        b.append(f'<path d="M {x0 + 170} 450 L {x0 + 200} 450 L {x0 + 90} 860 L {x0 + 60} 860 Z" fill="#fff" opacity="0.04"/>')
    # puerta (panel central)
    b.append('<rect x="790" y="470" width="18" height="380" fill="#0E0E0F"/><rect x="792" y="600" width="6" height="120" rx="3" fill="#9A9DA3"/>')
    b.append('<rect x="602" y="470" width="190" height="380" fill="none" stroke="#3A3C40" stroke-width="4"/>'
             '<rect x="808" y="470" width="190" height="380" fill="none" stroke="#3A3C40" stroke-width="4"/>')
    # vinilos en el vidrio
    b.append(f'<g opacity="0.92">{sym(380, 600, 150, "rojo")}</g>')
    b.append(text('REPUESTOS', 380, 730, 30, 'ArchivoExpBlack.ttf', W, anchor='middle', skew=0.21))
    b.append(text('PARA TU AUTO', 380, 766, 20, 'ArchivoBold.ttf', '#C9CCD1', anchor='middle', tracking=0.25, skew=0.21))
    b.append(text('ATENDEMOS', 700, 560, 14, 'PlexMono.ttf', '#C9CCD1', anchor='middle', tracking=0.15))
    b.append(text('[HORARIO]', 700, 590, 20, 'PlexMono.ttf', W, anchor='middle'))
    b.append(text('[TELÉFONO]', 1220, 640, 30, 'PlexMono.ttf', W, anchor='middle'))
    b.append(f'<rect x="1090" y="660" width="260" height="6" fill="{R}"/>')
    b.append(text('WHATSAPP / LLAMADAS', 1220, 700, 14, 'ArchivoBold.ttf', '#C9CCD1', anchor='middle', tracking=0.2))
    # lámparas
    for x in [330, 1270]:
        b.append(f'<path d="M {x - 160} 110 L {x + 160} 110 L {x + 300} 0 L {x - 300} 0 Z" fill="url(#cone)" opacity="0.0"/>')
    b.append('<rect x="0" y="0" width="1600" height="1000" fill="url(#vign)" opacity="0"/>')
    # pie
    b.append(f'<rect x="0" y="905" width="1600" height="95" fill="#111" opacity="0.75"/>')
    b.append(caption(W_, H_, 'Letrero de fachada', 'Caja de luz negra 6:1 con logo retroiluminado y franja roja · vinilos en vitrina', dark=True))
    return save('04-letrero', scene(W_, H_, ''.join(b), dark=True))


def card_front(w=540, h=300):
    lg, lh = logo_h(0, 0, w * 0.72)
    return (f'<rect width="{w}" height="{h}" rx="10" fill="{K}"/>'
            f'<g transform="translate({w * 0.14:.1f},{(h - lh) / 2:.1f})">{lg}</g>'
            f'<rect x="0" y="{h - 12}" width="{w}" height="12" fill="{R}"/>')


def card_back(w=540, h=300):
    rows = [('TEL', '[Teléfono / WhatsApp]'), ('DIR', '[Dirección del local]'), ('HOR', '[Horario de atención]')]
    out = [f'<rect width="{w}" height="{h}" rx="10" fill="#FFFFFF"/>',
           text('[Nombre Apellido]', 40, 72, 28, 'ArchivoExpBlack.ttf', K, skew=0.21),
           text('[Cargo]', 40, 104, 17, 'ArchivoRegular.ttf', '#5F636A'),
           sym(w - 70, 72, 70)]
    for i, (k, v) in enumerate(rows):
        y = 176 + i * 34
        out.append(text(k, 40, y, 15, 'PlexMono.ttf', R))
        out.append(text(v, 96, y, 15, 'PlexMono.ttf', K))
    out.append(f'<rect x="0" y="{h - 12}" width="{w}" height="12" fill="{K}"/><rect x="0" y="{h - 12}" width="{w * 0.3}" height="12" fill="{R}"/>')
    return ''.join(out)


def board_tarjetas():
    W_, H_ = 1600, 1000
    b = ['<defs><filter id="cardsh" filterUnits="userSpaceOnUse" x="-500" y="-500" width="3000" height="2000">'
         '<feGaussianBlur stdDeviation="16"/></filter></defs>']
    for (x, y, rot, fn) in [(230, 250, -8, card_back), (760, 330, 6, card_front), (260, 600, 4, card_front), (820, 610, -5, card_back)]:
        b.append(f'<g transform="translate({x},{y}) rotate({rot},270,150)">'
                 f'<rect x="6" y="22" width="540" height="300" rx="10" fill="#000" opacity="0.45" filter="url(#cardsh)"/>'
                 f'{fn()}</g>')
    # sticker redondo
    b.append('<g transform="translate(1400,230)"><circle r="120" fill="#000" opacity="0.4" filter="url(#cardsh)" transform="translate(4,14)"/>'
             f'<circle r="120" fill="{K}"/><circle r="108" fill="none" stroke="{R}" stroke-width="5"/>{sym(0, -20, 140)}'
             + text('AUTOPARTES', 0, 70, 14, 'ArchivoBold.ttf', W, anchor='middle', tracking=0.3, skew=0.21) + '</g>')
    b.append(caption(W_, H_, 'Tarjetas de presentación', '9 × 5 cm · frente negro con logo, dorso blanco con datos · sticker redondo de 8 cm', dark=True))
    return save('05-tarjetas', scene(W_, H_, ''.join(b), dark=True))


def board_redes():
    W_, H_ = 1600, 1000
    b = []
    # Post 1: producto
    def post(x, y, s, kind):
        o = [f'<g transform="translate({x},{y}) scale({s})">',
             '<rect x="8" y="24" width="1080" height="1080" fill="#000" opacity="0.35" filter="url(#floor)"/>',
             f'<clipPath id="pc{kind}"><rect width="1080" height="1080"/></clipPath><g clip-path="url(#pc{kind})">']
        if kind == 'producto':
            o.append(f'<rect width="1080" height="1080" fill="{K}"/>')
            o.append('<rect x="0" y="0" width="1080" height="1080" fill="url(#studioDark)" opacity="0.8"/>')
            o.append(f'<polygon points="0,1080 0,760 1080,560 1080,1080" fill="{R}"/>')
            o.append('<rect x="240" y="200" width="600" height="400" rx="24" fill="#1F2023" stroke="#3A3C40" stroke-width="4" stroke-dasharray="14 10"/>')
            o.append(text('[FOTO DEL PRODUCTO]', 540, 410, 34, 'PlexMono.ttf', '#8A8E95', anchor='middle'))
            o.append(text('[NOMBRE DEL PRODUCTO]', 70, 900, 56, 'ArchivoExpBlack.ttf', W, skew=0.21))
            o.append(text('[PRECIO]', 70, 990, 64, 'PlexMono.ttf', W))
            lg, _ = logo_h(70, 80, 440)
            o.append(lg)
        else:
            o.append(f'<rect width="1080" height="1080" fill="{R}"/>')
            o.append(f'<g opacity="0.12">{sym(800, 760, 900, "negro")}</g>')
            o.append(text('¿BUSCAS UN', 80, 380, 92, 'ArchivoExpBlack.ttf', W, skew=0.21))
            o.append(text('REPUESTO?', 80, 490, 92, 'ArchivoExpBlack.ttf', K, skew=0.21))
            o.append(text('Escríbenos con la marca, modelo y año', 84, 600, 36, 'ArchivoRegular.ttf', W))
            o.append(text('de tu vehículo y te lo cotizamos.', 84, 650, 36, 'ArchivoRegular.ttf', W))
            o.append(f'<rect x="80" y="760" width="520" height="100" rx="50" fill="{K}"/>')
            o.append(text('[WHATSAPP]', 340, 826, 40, 'PlexMono.ttf', W, anchor='middle'))
            lg, _ = logo_h(80, 930, 440, dark=True, variant='negro')
            o.append(lg)
        o.append('</g></g>')
        return ''.join(o)
    b.append(post(150, 110, 0.6, 'producto'))
    b.append(post(850, 110, 0.6, 'consulta'))
    b.append(caption(W_, H_, 'Redes sociales', 'Plantillas de publicación 1080 × 1080 · producto con precio y llamado a cotizar'))
    return save('06-redes', scene(W_, H_, ''.join(b)))

import sys
from common import scene, save, caption
from polo import polo

def board_polo():
    W_, H_ = 1600, 1000
    b = f'<g transform="translate(40,20) scale(0.76)">{polo("pf", True)}</g>'
    b += f'<g transform="translate(800,20) scale(0.76)">{polo("pb", False)}</g>'
    b += caption(W_, H_, 'Polo oficial', 'Piqué negro · símbolo bordado 8 cm en el pecho · logo vertical en la espalda, 28 cm')
    return save('01-polo', scene(W_, H_, b))

from garments import shirt, jacket, cap
from apps import board_letrero, board_tarjetas, board_redes
from brand import board_portada, board_logo, board_colores

def board_camisa():
    W_, H_ = 1600, 1000
    b = f'<g transform="translate(60,24) scale(0.72)">{shirt("sf", True)}</g>'
    b += f'<g transform="translate(820,24) scale(0.72)">{shirt("sb", False)}</g>'
    b += caption(W_, H_, 'Camisa de trabajo', 'Drill gris carbón con canesú negro y vivo rojo · nombre y símbolo bordados · logo en la espalda, 30 cm')
    return save('02-camisa', scene(W_, H_, b))

def board_casaca():
    W_, H_ = 1600, 1000
    b = f'<g transform="translate(70,24) scale(0.72)">{jacket("jk")}</g>'
    b += f'<g transform="translate(830,150) scale(0.7)">{cap("cp")}</g>'
    b += caption(W_, H_, 'Casaca y gorra', 'Softshell negra con cierre rojo · gorra negra con símbolo bordado 6 cm y ribete rojo en la visera')
    return save('03-casaca-gorra', scene(W_, H_, b))

if __name__ == '__main__':
    for n in sys.argv[1:]:
        print(globals()['board_' + n]())

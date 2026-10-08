import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build'))
from textpath import text_path
from em3 import mark, R, K, W

SYM = dict()

def tp(font, t, size, x=0, y=0, tracking=0.0, anchor='start', fill=K):
    d, w, b = text_path(font, t, size, x, y, anchor=anchor, tracking=tracking)
    return f'<path d="{d}" fill="{fill}"/>', w, b

def horiz(font, dark=False, sub_font='PlexMono.ttf', s=200, wsize=None, track=0.0, sub='E&M · AUTOPARTES MULTIMARCA', cE=None):
    fg = W if dark else K
    sym, sb = mark(s=s, cE=cE or fg, cM=R, **SYM)
    sw = sb[2]
    x0 = sw + s * 0.32
    wsize = wsize or s * 0.42
    # palabra: alinear su altura de mayúsculas con la parte superior del símbolo
    _, ww, wb = tp(font, 'MULTIREPUESTO', wsize, 0, 0, tracking=track)
    cap = -wb[1]
    word, ww, wb = tp(font, 'MULTIREPUESTO', wsize, x0, cap + s*0.04, tracking=track, fill=fg)
    # subtítulo: ajustado al ancho de la palabra, alineado con la base del símbolo
    _, w1, _ = tp(sub_font, sub, 100, 0, 0, tracking=0.25)
    ssize = min(100 * (ww) / w1, s*0.14)
    sub_p, sw2, sbb = tp(sub_font, sub, ssize, x0, s - s*0.005, tracking=0.25, fill=(fg if dark else '#5F636A'))
    bar = f'<rect x="{x0:.1f}" y="{s*0.62:.1f}" width="{ww:.1f}" height="{s*0.025:.1f}" fill="{R}"/>'
    return sym + word + bar + sub_p, (0, 0, max(wb[2], sbb[2]), s)

def vert(font, dark=False, s=200, track=0.0):
    fg = W if dark else K
    sym, sb = mark(s=s, cE=fg, cM=R, **SYM)
    sw = sb[2]
    _, ww, wb = tp(font, 'MULTIREPUESTO', 100, 0, 0, tracking=track)
    wsize = 100 * sw * 1.25 / ww
    word, ww, wb = tp(font, 'MULTIREPUESTO', wsize, sw/2, s + s*0.28 + (-wb[1])*wsize/100, tracking=track, anchor='middle', fill=fg)
    sub, sw2, sbb = tp('PlexMono.ttf', 'E&M · AUTOPARTES MULTIMARCA', wsize*0.32, sw/2, wb[3] + wsize*0.55, tracking=0.25, anchor='middle', fill=(fg if dark else '#5F636A'))
    return sym + word + sub, (min(wb[0], sbb[0]), 0, max(wb[2], sbb[2]), sbb[3])

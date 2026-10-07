"""Convierte texto a trazos SVG (con kerning) usando HarfBuzz + fontTools."""
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fuentes')
_cache = {}


def _font(name):
    if name not in _cache:
        path = os.path.join(FONT_DIR, name)
        blob = hb.Blob.from_file_path(path)
        _cache[name] = (TTFont(path), hb.Font(hb.Face(blob)))
    return _cache[name]


def text_path(fontname, text, size, x=0.0, y=0.0, tracking=0.0, anchor='start', skew=0.0):
    """Devuelve (d, ancho, (xmin, ymin, xmax, ymax)). y = línea base. tracking en em."""
    tt, hbf = _font(fontname)
    upm = tt['head'].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": False})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = size / upm
    advances = []
    total = 0
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        adv = pos.x_advance + (tracking * upm if i < len(buf.glyph_infos) - 1 else 0)
        advances.append((info, pos, total))
        total += adv
    width = total * s
    if anchor == 'middle':
        x -= width / 2
    elif anchor == 'end':
        x -= width
    pen = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    bp = BoundsPen(gs)
    k = -skew  # skew horizontal: x' = x + k*(-y) en coords de fuente
    for info, pos, off in advances:
        name = order[info.codepoint]
        ox = x + (off + pos.x_offset) * s
        oy = y - pos.y_offset * s
        m = (s, 0, s * skew, -s, ox, oy)
        gs[name].draw(TransformPen(pen, m))
        gs[name].draw(TransformPen(bp, m))
    return pen.getCommands(), width, bp.bounds

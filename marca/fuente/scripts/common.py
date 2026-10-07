"""Piezas comunes para mockups: filtros, fondos y logos embebibles."""
import os
from logo import symbol, wordmark, horizontal, vertical, SYM_W, SYM_H, R, K, W
from textpath import text_path

OUT = os.path.join(os.path.dirname(__file__), 'out', 'mockups')
os.makedirs(OUT, exist_ok=True)

DEFS = '''
<filter id="fabric" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.10 0"/>
</filter>
<filter id="fabricDark" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="9" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.22 0"/>
</filter>
<filter id="soft" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="soft6" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="soft3" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="floor" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000"><feGaussianBlur stdDeviation="26"/></filter>
<filter id="emb" x="-10%" y="-10%" width="120%" height="120%">
  <feDropShadow dx="0" dy="1.6" stdDeviation="1.1" flood-color="#000" flood-opacity="0.75"/>
  <feDropShadow dx="0" dy="-0.6" stdDeviation="0.4" flood-color="#fff" flood-opacity="0.12"/>
</filter>
<filter id="print" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="2" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.35 -0.05" result="nn"/>
  <feComposite in="SourceGraphic" in2="nn" operator="out" result="cut"/>
  <feMerge><feMergeNode in="cut"/></feMerge>
</filter>
<radialGradient id="studio" cx="50%" cy="38%" r="75%">
  <stop offset="0" stop-color="#F4F4F5"/><stop offset="0.6" stop-color="#E2E2E4"/><stop offset="1" stop-color="#C9C9CC"/>
</radialGradient>
<radialGradient id="studioDark" cx="50%" cy="40%" r="75%">
  <stop offset="0" stop-color="#2A2B2E"/><stop offset="0.65" stop-color="#16171A"/><stop offset="1" stop-color="#0A0A0B"/>
</radialGradient>
'''


def sym(x, y, width, variant='principal'):
    """Símbolo centrado en (x,y) con ancho dado."""
    s = width / SYM_W
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.4f})">{symbol(variant)}</g>'


def logo_h(x, y, width, dark=True, variant='principal'):
    """Logo horizontal con esquina sup-izq en (x,y)."""
    w, h, body = horizontal(dark, variant)
    s = width / w
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.4f})">{body}</g>', h * s


def logo_v(cx, y, width, dark=True, variant='principal'):
    w, h, body = vertical(dark, variant)
    s = width / w
    return f'<g transform="translate({cx - width / 2:.2f},{y:.2f}) scale({s:.4f})">{body}</g>', h * s


def text(t, x, y, size, font='ArchivoBold.ttf', fill=K, anchor='start', tracking=0.0, skew=0.0):
    d, w, _ = text_path(font, t, size, x, y, anchor=anchor, tracking=tracking, skew=skew)
    return f'<path d="{d}" fill="{fill}"/>'


def caption(W_, H_, title, sub, dark=False):
    """Pie de lámina: marca pequeña + título."""
    col = '#FFFFFF' if dark else K
    mut = '#9A9DA3' if dark else '#5F636A'
    out = sym(84, H_ - 70, 64)
    out += text(title.upper(), 132, H_ - 72, 22, 'ArchivoExpBlack.ttf', col, tracking=0.01, skew=0.21)
    out += text(sub, 132, H_ - 44, 15, 'ArchivoRegular.ttf', mut)
    out += text('MULTIREPUESTO E&M · MANUAL DE MARCA', W_ - 52, H_ - 52, 13, 'PlexMono.ttf', mut, anchor='end', tracking=0.08)
    return out


def scene(W_, H_, body, dark=False):
    bg = 'url(#studioDark)' if dark else 'url(#studio)'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}">'
            f'<defs>{DEFS}</defs><rect width="{W_}" height="{H_}" fill="{bg}"/>{body}</svg>')


def save(name, svgtext):
    p = os.path.join(OUT, name + '.svg')
    with open(p, 'w') as f:
        f.write(svgtext)
    return p

"""Símbolo E→M definitivo: la E con ranuras fresadas; la M es la misma pieza girada 90°."""
R = '#D7141A'; K = '#111111'; W = '#FFFFFF'
P = dict(t=0.29, ro=1.6, rend=0.12, gap=0.16)

def E_path(s=100, t=P['t'], ro=P['ro'], rend=P['rend']):
    w = h = s; T = t * s; g = (h - 3 * T) / 2; RE = rend * T; RO = ro * T; q = g / 2
    f = lambda v: f'{v:.3f}'
    d = [f'M0 0', f'H{f(w - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w)} {f(RE)}',
         f'V{f(T - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w - RE)} {f(T)}',
         f'H{f(T + q)}', f'A{f(q)} {f(q)} 0 0 0 {f(T + q)} {f(T + g)}',
         f'H{f(w - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w)} {f(T + g + RE)}',
         f'V{f(2 * T + g - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w - RE)} {f(2 * T + g)}',
         f'H{f(T + q)}', f'A{f(q)} {f(q)} 0 0 0 {f(T + q)} {f(2 * T + 2 * g)}',
         f'H{f(w - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w)} {f(2 * T + 2 * g + RE)}',
         f'V{f(h - RE)}', f'A{f(RE)} {f(RE)} 0 0 1 {f(w - RE)} {f(h)}',
         f'H{f(RO)}', f'A{f(RO)} {f(RO)} 0 0 1 0 {f(h - RO)}', 'Z']
    return ''.join(d)

def mark(s=100, cE=K, cM=R, gap=P['gap'], **kw):
    d = E_path(s); g = gap * s
    return (f'<path d="{d}" fill="{cE}"/>'
            f'<g transform="translate({2 * s + g:.3f},0) rotate(90)"><path d="{d}" fill="{cM}"/></g>'), (0, 0, 2 * s + g, s)

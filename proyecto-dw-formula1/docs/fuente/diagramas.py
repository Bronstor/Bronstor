"""Diagramas del modelo conceptual y lógico (SVG) generados desde modelo.py.

exportar_png(carpeta) escribe los SVG y los convierte a PNG con Chromium
(capturar_svg.js) para insertarlos en el informe.
"""
import subprocess
from pathlib import Path

from modelo import JERARQUIAS, TABLAS

BASE = Path(__file__).resolve().parent
ROJO, AZUL, TINTA, GRIS = "#8b1a2b", "#2b3a55", "#1d2433", "#5b6475"
COLOR_CLAVE = {"PK": ROJO, "FK": "#2f5f9e", "NK": "#5e4a8f", "DD": "#8a5200"}
FUENTE = "Arial, Liberation Sans, sans-serif"


def svg_conceptual():
    w_dim, h_dim = 250, 140
    dims = [  # (tabla, x, y)
        ("dim_tiempo", 30, 20), ("dim_carrera", 375, 20), ("dim_circuito", 720, 20),
        ("dim_piloto", 30, 474), ("dim_escuderia", 375, 474), ("dim_estado", 720, 474),
    ]
    fx, fy, fw, fh = 300, 200, 400, 214
    p = [f'<svg viewBox="0 0 1000 622" xmlns="http://www.w3.org/2000/svg" font-family="{FUENTE}">',
         '<rect width="1000" height="622" fill="#fff"/>']
    anclas_hecho = [fx + 70, fx + fw / 2, fx + fw - 70]
    for i, (t, x, y) in enumerate(dims):
        arriba = y < fy
        x1 = x + w_dim / 2
        y1 = y + h_dim if arriba else y
        x2 = anclas_hecho[i % 3]
        y2 = fy if arriba else fy + fh
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#8796ad" stroke-width="2"/>')
        dy1 = 16 if arriba else -8
        dy2 = -8 if arriba else 18
        p.append(f'<text x="{x1 + 8}" y="{y1 + dy1}" font-size="14" font-weight="600" fill="{GRIS}">1</text>')
        p.append(f'<text x="{x2 + 8}" y="{y2 + dy2}" font-size="14" font-weight="600" fill="{GRIS}">N</text>')
    for t, x, y in dims:
        nombre, niveles = JERARQUIAS[t]
        p.append(f'<rect x="{x}" y="{y}" width="{w_dim}" height="{h_dim}" rx="8" fill="#eef3fa" stroke="#8aa1c1" stroke-width="1.5"/>')
        p.append(f'<path d="M{x} {y + 8} a8 8 0 0 1 8 -8 h{w_dim - 16} a8 8 0 0 1 8 8 v22 h-{w_dim} z" fill="{AZUL}"/>')
        p.append(f'<text x="{x + 12}" y="{y + 21}" font-size="15" font-weight="700" fill="#fff">Dimensión {nombre}</text>')
        for j, nivel in enumerate(niveles):
            ty = y + 50 + j * 15.5
            tx = x + 14 + j * 13
            prefijo = "↳ " if j else ""
            peso = "600" if j == len(niveles) - 1 else "400"
            p.append(f'<text x="{tx}" y="{ty}" font-size="13.5" font-weight="{peso}" fill="{TINTA}">{prefijo}{nivel}</text>')
    p.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="#fdf1f3" stroke="{ROJO}" stroke-width="2"/>')
    p.append(f'<path d="M{fx} {fy + 10} a10 10 0 0 1 10 -10 h{fw - 20} a10 10 0 0 1 10 10 v36 h-{fw} z" fill="{ROJO}"/>')
    p.append(f'<text x="{fx + fw / 2}" y="{fy + 20}" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">HECHO: RESULTADO DE CARRERA</text>')
    p.append(f'<text x="{fx + fw / 2}" y="{fy + 38}" font-size="12" fill="#fde3e8" text-anchor="middle">Grano: un piloto con un auto en un Gran Premio</text>')
    medidas = [
        ("Puntos oficiales", "Puntos sistema actual"),
        ("Posición de salida", "Posición final"),
        ("Posiciones ganadas", "Vueltas completadas"),
        ("Tiempo de carrera", "Vuelta más rápida"),
        ("Edad del piloto", "Puntos acumulados"),
        ("Victoria · Podio · Pole", "Finalizó · Abandono"),
    ]
    for j, (a, b) in enumerate(medidas):
        ty = fy + 72 + j * 24
        p.append(f'<text x="{fx + 22}" y="{ty}" font-size="13.5" fill="{TINTA}">• {a}</text>')
        p.append(f'<text x="{fx + fw / 2 + 10}" y="{ty}" font-size="13.5" fill="{TINTA}">• {b}</text>')
    p.append("</svg>")
    return "\n".join(p)


def svg_logico():
    fila, cab, pie = 19, 28, 6
    w_dim, w_fact = 330, 390
    fact_x, fact_y = 420, 20
    lado = {  # tabla: (x, y, carril)  carril = x de la línea vertical del conector
        "dim_tiempo": (20, 20, 370), "dim_carrera": (20, 302, 385), "dim_estado": (20, 546, 400),
        "dim_circuito": (880, 20, 860), "dim_piloto": (880, 264, 845), "dim_escuderia": (880, 508, 830),
    }
    fk_de = {"dim_tiempo": "sk_tiempo", "dim_carrera": "sk_carrera", "dim_circuito": "sk_circuito",
             "dim_piloto": "sk_piloto", "dim_escuderia": "sk_escuderia", "dim_estado": "sk_estado"}
    separadores = {7, 10, 24, 31}  # inicio de: degeneradas, métricas, indicadores, auditoría

    def tabla(nombre, x, y, w, es_hecho):
        cols = TABLAS[nombre]["columnas"]
        h = cab + len(cols) * fila + pie
        borde = ROJO if es_hecho else "#8aa1c1"
        fondo_cab = ROJO if es_hecho else AZUL
        s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{borde}" stroke-width="1.6"/>',
             f'<path d="M{x} {y + 6} a6 6 0 0 1 6 -6 h{w - 12} a6 6 0 0 1 6 6 v{cab - 6} h-{w} z" fill="{fondo_cab}"/>',
             f'<text x="{x + 12}" y="{y + 19}" font-size="14.5" font-weight="700" fill="#fff">{nombre}</text>']
        for i, (col, tipo, clave, nulo, *_r) in enumerate(cols):
            ty = y + cab + i * fila
            if i % 2:
                s.append(f'<rect x="{x + 1}" y="{ty}" width="{w - 2}" height="{fila}" fill="#f4f6fa"/>')
            if es_hecho and i in separadores:
                s.append(f'<line x1="{x}" y1="{ty}" x2="{x + w}" y2="{ty}" stroke="#d9a3ae" stroke-width="1"/>')
            if clave:
                s.append(f'<text x="{x + 10}" y="{ty + 13.5}" font-size="10" font-weight="700" fill="{COLOR_CLAVE[clave]}">{clave}</text>')
            peso = "600" if clave in ("PK", "FK") else "400"
            s.append(f'<text x="{x + 38}" y="{ty + 13.5}" font-size="13" font-weight="{peso}" fill="{TINTA}">{col}</text>')
            tipo_txt = tipo + ("" if not nulo else " ?")
            s.append(f'<text x="{x + w - 10}" y="{ty + 13.5}" font-size="11.5" fill="{GRIS}" text-anchor="end">{tipo_txt}</text>')
        return s, h

    cuerpo = []
    fact_cols = [c[0] for c in TABLAS["fact_resultado_carrera"]["columnas"]]
    for nombre, (x, y, carril) in lado.items():
        izquierda = x < fact_x
        y_pk = y + cab + fila / 2
        y_fk = fact_y + cab + fact_cols.index(fk_de[nombre]) * fila + fila / 2
        x_dim = x + w_dim if izquierda else x
        x_hecho = fact_x if izquierda else fact_x + w_fact
        cuerpo.append(f'<path d="M{x_dim} {y_pk} H{carril} V{y_fk} H{x_hecho}" fill="none" stroke="#7d8aa0" stroke-width="1.6"/>')
        d = 1 if izquierda else -1
        for off in (8, 13):  # lado "1": dos barras junto a la dimensión
            bx = x_dim + d * off
            cuerpo.append(f'<line x1="{bx}" y1="{y_pk - 6}" x2="{bx}" y2="{y_pk + 6}" stroke="#7d8aa0" stroke-width="1.6"/>')
        bx = x_hecho - d * 12  # lado "N": pata de gallo junto a la tabla de hechos
        for dy in (-7, 0, 7):
            cuerpo.append(f'<line x1="{bx}" y1="{y_fk}" x2="{x_hecho}" y2="{y_fk + dy}" stroke="#7d8aa0" stroke-width="1.6"/>')
    for nombre, (x, y, _c) in lado.items():
        s, _h = tabla(nombre, x, y, w_dim, False)
        cuerpo += s
    s, h_fact = tabla("fact_resultado_carrera", fact_x, fact_y, w_fact, True)
    cuerpo += s
    alto = max(fact_y + h_fact, 546 + cab + 4 * fila + pie) + 20
    ancho = 880 + w_dim + 20
    return (f'<svg viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" font-family="{FUENTE}">\n'
            f'<rect width="{ancho}" height="{alto}" fill="#fff"/>\n' + "\n".join(cuerpo) + "\n</svg>")


def exportar_png(carpeta):
    """Escribe conceptual.png y logico.png en `carpeta` y devuelve sus rutas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = {}
    for nombre, svg, ancho in (("conceptual", svg_conceptual(), 1600), ("logico", svg_logico(), 2000)):
        svg_path = carpeta / f"{nombre}.svg"
        png_path = carpeta / f"{nombre}.png"
        svg_path.write_text(svg, encoding="utf-8")
        subprocess.run(["node", str(BASE / "capturar_svg.js"), str(svg_path), str(png_path), str(ancho)], check=True)
        rutas[nombre] = png_path
    return rutas


if __name__ == "__main__":
    print(exportar_png(BASE / "build"))

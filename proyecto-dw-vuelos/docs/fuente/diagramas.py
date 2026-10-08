"""Diagramas de los modelos conceptual, lógico y físico del DataMart (PNG).

Las tablas y columnas se leen de modelo_fisico.json, exportado del catálogo
de PostgreSQL después de ejecutar sql/01 y sql/02. Cada diagrama se dibuja
como SVG y se convierte a PNG con Chromium (capturar_svg.js; requiere
NODE_PATH apuntando a los módulos globales de Node).
"""
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
FUENTE = "Arial, Liberation Sans, sans-serif"
ROJO, AZUL, TINTA, GRIS = "#8b1a2b", "#2b3a55", "#1d2433", "#5b6475"
COLOR_CLAVE = {"PK": ROJO, "FK": "#2f5f9e", "UK": "#5e4a8f", "NK": "#5e4a8f", "DD": "#8a5200"}

FILA, CAB, PIE = 22, 32, 6
POSICION = {  # tabla: (x, y, ancho)
    "fact_vuelo": (490, 20, 470),
    "dim_fecha": (20, 20, 380),
    "dim_hora": (20, 330, 380),
    "dim_aerolinea": (1050, 20, 380),
    "dim_aeropuerto": (1050, 170, 380),
    "dim_motivo_cancelacion": (1050, 450, 380),
}
# (columna FK de fact_vuelo, tabla destino, x del tramo vertical del conector)
CONECTORES = [
    ("sk_fecha", "dim_fecha", 420),
    ("sk_hora_salida", "dim_hora", 455),
    ("sk_aerolinea", "dim_aerolinea", 1024),
    ("sk_aeropuerto_origen", "dim_aeropuerto", 1006),
    ("sk_aeropuerto_destino", "dim_aeropuerto", 989),
    ("sk_motivo_cancelacion", "dim_motivo_cancelacion", 972),
]
DEGENERADAS = {"numero_vuelo", "matricula_avion", "salida_programada"}


def _modelo():
    return {t["tabla"]: t for t in json.loads((BASE / "modelo_fisico.json").read_text(encoding="utf-8"))}


def _envolver(cuerpo, ancho, alto):
    return (f'<svg viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" font-family="{FUENTE}">\n'
            f'<rect width="{ancho}" height="{alto}" fill="#fff"/>\n' + "\n".join(cuerpo) + "\n</svg>")


# ---------------------------------------------------------------------------
# Modelo conceptual: hecho, dimensiones y jerarquías
# ---------------------------------------------------------------------------
def svg_conceptual():
    w_dim, h_dim = 280, 150
    dims = [  # (título, subtítulo, niveles, x, y)
        ("Fecha", "", ["Año", "Trimestre", "Mes", "Fecha"], 20, 20),
        ("Hora de salida", "", ["Franja horaria", "Hora"], 360, 20),
        ("Aerolínea", "", ["Aerolínea"], 700, 20),
        ("Aeropuerto de origen", "rol de Aeropuerto", ["Región", "Estado", "Ciudad", "Aeropuerto"], 20, 480),
        ("Aeropuerto de destino", "rol de Aeropuerto", ["Región", "Estado", "Ciudad", "Aeropuerto"], 360, 480),
        ("Motivo de cancelación", "", ["Motivo"], 700, 480),
    ]
    fx, fy, fw, fh = 290, 215, 420, 220
    p = []
    anclas = [fx + 70, fx + fw / 2, fx + fw - 70]
    for i, (_t, _s, _n, x, y) in enumerate(dims):
        arriba = y < fy
        x1, y1 = x + w_dim / 2, (y + h_dim if arriba else y)
        x2, y2 = anclas[i % 3], (fy if arriba else fy + fh)
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7d8aa0" stroke-width="2"/>')
        p.append(f'<text x="{x1 + 8}" y="{y1 + (18 if arriba else -8)}" font-size="16" font-weight="700" fill="{GRIS}">1</text>')
        p.append(f'<text x="{x2 + 8}" y="{y2 + (-8 if arriba else 20)}" font-size="16" font-weight="700" fill="{GRIS}">N</text>')
    for titulo, subtitulo, niveles, x, y in dims:
        p.append(f'<rect x="{x}" y="{y}" width="{w_dim}" height="{h_dim}" rx="8" fill="#eef2f8" stroke="#7f93b3" stroke-width="1.5"/>')
        p.append(f'<path d="M{x} {y + 8} a8 8 0 0 1 8 -8 h{w_dim - 16} a8 8 0 0 1 8 8 v26 h-{w_dim} z" fill="{AZUL}"/>')
        p.append(f'<text x="{x + 12}" y="{y + 24}" font-size="17" font-weight="700" fill="#fff">{titulo}</text>')
        y0 = y + 56
        if subtitulo:
            p.append(f'<text x="{x + 12}" y="{y0}" font-size="14" font-style="italic" fill="{GRIS}">({subtitulo})</text>')
            y0 += 20
        for j, nivel in enumerate(niveles):
            prefijo = "↳ " if j else ""
            peso = "700" if j == len(niveles) - 1 else "400"
            p.append(f'<text x="{x + 14 + j * 16}" y="{y0 + j * 19}" font-size="16" font-weight="{peso}" fill="{TINTA}">{prefijo}{nivel}</text>')
    # Día de la semana: segunda jerarquía de Fecha
    p.append(f'<text x="{20 + 150}" y="{20 + 56}" font-size="14" fill="{GRIS}">+ Día de la semana</text>')
    # Hecho
    p.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="#fbf0f2" stroke="{ROJO}" stroke-width="2"/>')
    p.append(f'<path d="M{fx} {fy + 10} a10 10 0 0 1 10 -10 h{fw - 20} a10 10 0 0 1 10 10 v40 h-{fw} z" fill="{ROJO}"/>')
    p.append(f'<text x="{fx + fw / 2}" y="{fy + 23}" font-size="18" font-weight="700" fill="#fff" text-anchor="middle">HECHO: VUELO</text>')
    p.append(f'<text x="{fx + fw / 2}" y="{fy + 42}" font-size="13.5" fill="#fbe3e8" text-anchor="middle">Grano: un vuelo programado de una aerolínea en una fecha</text>')
    medidas = [("Retraso de salida", "Retraso de llegada"), ("Minutos por causa", "Tiempos de rodaje"),
               ("Tiempo de vuelo", "Distancia"), ("Cancelado", "Desviado"), ("Retrasado", "Puntual")]
    for j, (a, b) in enumerate(medidas):
        ty = fy + 78 + j * 30
        p.append(f'<text x="{fx + 26}" y="{ty}" font-size="16" fill="{TINTA}">• {a}</text>')
        p.append(f'<text x="{fx + fw / 2 + 14}" y="{ty}" font-size="16" fill="{TINTA}">• {b}</text>')
    return _envolver(p, 1000, 650)


# ---------------------------------------------------------------------------
# Modelos lógico y físico: tablas con columnas y conectores 1:N
# ---------------------------------------------------------------------------
def _tablas(modelo, describir):
    """describir(tabla, columna) -> (etiquetas de clave, texto de la derecha, marca NN)."""
    partes = []

    def fila_y(tabla, columna):
        _x, y, _w = POSICION[tabla]
        nombres = [c["columna"] for c in modelo[tabla]["columnas"]]
        return y + CAB + nombres.index(columna) * FILA + FILA / 2

    fx, _fy, fw = POSICION["fact_vuelo"]
    for col_fk, destino, carril in CONECTORES:
        dx, _dy, dw = POSICION[destino]
        izquierda = dx < fx
        pk = next(c["columna"] for c in modelo[destino]["columnas"] if c["pk"])
        y_pk, y_fk = fila_y(destino, pk), fila_y("fact_vuelo", col_fk)
        x_dim = dx + dw if izquierda else dx
        x_hecho = fx if izquierda else fx + fw
        d = 1 if izquierda else -1
        partes.append(f'<path d="M{x_dim} {y_pk} H{carril} V{y_fk} H{x_hecho}" fill="none" stroke="#6f7c91" stroke-width="1.6"/>')
        for off in (8, 13):  # lado 1
            partes.append(f'<line x1="{x_dim + d * off}" y1="{y_pk - 6}" x2="{x_dim + d * off}" y2="{y_pk + 6}" stroke="#6f7c91" stroke-width="1.6"/>')
        for dy in (-7, 0, 7):  # lado N (pata de gallo)
            partes.append(f'<line x1="{x_hecho - d * 12}" y1="{y_fk}" x2="{x_hecho}" y2="{y_fk + dy}" stroke="#6f7c91" stroke-width="1.6"/>')

    for tabla, (x, y, w) in POSICION.items():
        columnas = modelo[tabla]["columnas"]
        es_hecho = tabla.startswith("fact")
        h = CAB + len(columnas) * FILA + PIE
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fff" stroke="{ROJO if es_hecho else "#7f93b3"}" stroke-width="1.6"/>')
        partes.append(f'<path d="M{x} {y + 5} a5 5 0 0 1 5 -5 h{w - 10} a5 5 0 0 1 5 5 v{CAB - 5} h-{w} z" fill="{ROJO if es_hecho else AZUL}"/>')
        partes.append(f'<text x="{x + 10}" y="{y + 22}" font-size="16.5" font-weight="700" fill="#fff">{tabla}</text>')
        for i, c in enumerate(columnas):
            ty = y + CAB + i * FILA
            if i % 2:
                partes.append(f'<rect x="{x + 1}" y="{ty}" width="{w - 2}" height="{FILA}" fill="#f2f4f8"/>')
            claves, derecha, nn = describir(tabla, c)
            if claves:
                partes.append(f'<text x="{x + 8}" y="{ty + 16}" font-size="11.5" font-weight="700" fill="{COLOR_CLAVE[claves[0]]}">{" ".join(claves)}</text>')
            peso = "700" if c["pk"] or c["fk"] else "400"
            partes.append(f'<text x="{x + 62}" y="{ty + 16}" font-size="15" font-weight="{peso}" fill="{TINTA}">{c["columna"]}</text>')
            if derecha:
                partes.append(f'<text x="{x + w - (42 if nn is not None else 10)}" y="{ty + 16}" font-size="13.5" fill="{GRIS}" text-anchor="end">{derecha}</text>')
            if nn:
                partes.append(f'<text x="{x + w - 8}" y="{ty + 16}" font-size="11.5" font-weight="700" fill="{GRIS}" text-anchor="end">NN</text>')

    alto = max(y + CAB + len(modelo[t]["columnas"]) * FILA + PIE for t, (x, y, w) in POSICION.items()) + 20
    ancho = max(x + w for x, y, w in POSICION.values()) + 20
    return _envolver(partes, ancho, alto)


def svg_logico():
    """Tablas, atributos, claves y relaciones, sin tipos de datos del DBMS."""
    def describir(tabla, c):
        nombre = c["columna"]
        if c["pk"]:
            return ["PK"], "clave sustituta", None
        if c["fk"]:
            return ["FK"], "→ " + c["fk"].split(".")[-1], None
        if tabla.startswith("fact"):
            if nombre in DEGENERADAS:
                return ["DD"], "dimensión degenerada", None
            if nombre.startswith("es_"):
                return [], "indicador 0/1", None
            if nombre.endswith("_min"):
                return [], "métrica (minutos)", None
            if nombre == "distancia_millas":
                return [], "métrica (millas)", None
            return [], "auditoría ETL", None
        if c["uk"]:
            return ["NK"], "clave natural", None
        return [], "", None
    return _tablas(_modelo(), describir)


def svg_fisico():
    """Tablas con columnas, tipos de datos de PostgreSQL, claves y NOT NULL."""
    def describir(_tabla, c):
        claves = [k for k, activo in (("PK", c["pk"]), ("FK", bool(c["fk"])), ("UK", c["uk"] and not c["pk"])) if activo]
        tipo = (c["tipo"].replace("CHARACTER VARYING", "VARCHAR").replace("CHARACTER(", "CHAR(")
                .replace(" WITHOUT TIME ZONE", "")) + (" IDENTITY" if c["identity"] else "")
        return claves, tipo, c["not_null"]
    return _tablas(_modelo(), describir)


def exportar_png(nombre, carpeta=BASE / "build"):
    """nombre: 'conceptual', 'logico' o 'fisico'. Devuelve la ruta del PNG."""
    generador, ancho = {"conceptual": (svg_conceptual, 1600), "logico": (svg_logico, 2000),
                        "fisico": (svg_fisico, 2000)}[nombre]
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    svg_path, png_path = carpeta / f"modelo_{nombre}.svg", carpeta / f"modelo_{nombre}.png"
    svg_path.write_text(generador(), encoding="utf-8")
    subprocess.run(["node", str(BASE / "capturar_svg.js"), str(svg_path), str(png_path), str(ancho)], check=True)
    return png_path


if __name__ == "__main__":
    for n in ("conceptual", "logico", "fisico"):
        print(exportar_png(n))

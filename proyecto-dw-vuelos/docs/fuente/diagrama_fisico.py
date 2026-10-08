"""Diagrama del modelo físico (tablas, columnas, tipos y claves) en PNG.

Lee modelo_fisico.json, exportado del catálogo de PostgreSQL después de
ejecutar sql/01 y sql/02, dibuja un SVG y lo convierte a PNG con Chromium
(capturar_svg.js, requiere NODE_PATH apuntando a los módulos globales).
"""
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
FUENTE = "Arial, Liberation Sans, sans-serif"
ROJO, AZUL, TINTA, GRIS = "#8b1a2b", "#2b3a55", "#1d2433", "#5b6475"

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


def tipo_corto(tipo):
    return (tipo.replace("CHARACTER VARYING", "VARCHAR")
                .replace("CHARACTER(", "CHAR(")
                .replace(" WITHOUT TIME ZONE", ""))


def svg():
    modelo = {t["tabla"]: t for t in json.loads((BASE / "modelo_fisico.json").read_text(encoding="utf-8"))}
    partes = []

    def fila_y(tabla, columna):
        x, y, _w = POSICION[tabla]
        nombres = [c["columna"] for c in modelo[tabla]["columnas"]]
        return y + CAB + nombres.index(columna) * FILA + FILA / 2

    # Conectores (debajo de las tablas)
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

    # Tablas
    for tabla, (x, y, w) in POSICION.items():
        columnas = modelo[tabla]["columnas"]
        es_hecho = tabla.startswith("fact")
        h = CAB + len(columnas) * FILA + PIE
        borde = ROJO if es_hecho else "#7f93b3"
        partes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#fff" stroke="{borde}" stroke-width="1.6"/>')
        partes.append(f'<path d="M{x} {y + 5} a5 5 0 0 1 5 -5 h{w - 10} a5 5 0 0 1 5 5 v{CAB - 5} h-{w} z" fill="{ROJO if es_hecho else AZUL}"/>')
        partes.append(f'<text x="{x + 10}" y="{y + 22}" font-size="16.5" font-weight="700" fill="#fff">{tabla}</text>')
        for i, c in enumerate(columnas):
            ty = y + CAB + i * FILA
            if i % 2:
                partes.append(f'<rect x="{x + 1}" y="{ty}" width="{w - 2}" height="{FILA}" fill="#f2f4f8"/>')
            claves = [k for k, activo in (("PK", c["pk"]), ("FK", bool(c["fk"])), ("UK", c["uk"] and not c["pk"])) if activo]
            if claves:
                color = ROJO if "PK" in claves else ("#2f5f9e" if "FK" in claves else "#5e4a8f")
                partes.append(f'<text x="{x + 8}" y="{ty + 16}" font-size="11.5" font-weight="700" fill="{color}">{" ".join(claves)}</text>')
            peso = "700" if c["pk"] or c["fk"] else "400"
            partes.append(f'<text x="{x + 62}" y="{ty + 16}" font-size="15" font-weight="{peso}" fill="{TINTA}">{c["columna"]}</text>')
            tipo = tipo_corto(c["tipo"]) + (" IDENTITY" if c["identity"] else "")
            partes.append(f'<text x="{x + w - 42}" y="{ty + 16}" font-size="13.5" fill="{GRIS}" text-anchor="end">{tipo}</text>')
            if c["not_null"]:
                partes.append(f'<text x="{x + w - 8}" y="{ty + 16}" font-size="11.5" font-weight="700" fill="{GRIS}" text-anchor="end">NN</text>')

    alto = max(y + CAB + len(modelo[t]["columnas"]) * FILA + PIE for t, (x, y, w) in POSICION.items()) + 20
    ancho = max(x + w for x, y, w in POSICION.values()) + 20
    return (f'<svg viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" font-family="{FUENTE}">\n'
            f'<rect width="{ancho}" height="{alto}" fill="#fff"/>\n' + "\n".join(partes) + "\n</svg>")


def exportar_png(carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    svg_path, png_path = carpeta / "modelo_fisico.svg", carpeta / "modelo_fisico.png"
    svg_path.write_text(svg(), encoding="utf-8")
    subprocess.run(["node", str(BASE / "capturar_svg.js"), str(svg_path), str(png_path), "2000"], check=True)
    return png_path


if __name__ == "__main__":
    print(exportar_png(BASE / "build"))

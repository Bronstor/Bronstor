"""Construye el informe de la primera presentación (HTML -> PDF).

Uso (desde esta carpeta):
    python3 construir_informe.py

Requiere Python 3, pypdf y Node.js con Playwright (Chromium). El resultado
se escribe en ../Primera_Presentacion_DW_Formula1.pdf.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader

from modelo import JERARQUIAS, TABLAS

BASE = Path(__file__).resolve().parent
SQL = BASE.parent.parent / "sql"
SALIDA_HTML = BASE / "build" / "informe.html"
SALIDA_PDF = BASE.parent / "Primera_Presentacion_DW_Formula1.pdf"

ROJO, AZUL, TINTA, GRIS = "#b3122e", "#24406b", "#1d2433", "#5b6475"
COLOR_CLAVE = {"PK": ROJO, "FK": "#2f6db5", "NK": "#6b4fa3", "DD": "#9a5b00"}


# ---------------------------------------------------------------------------
# Diagramas SVG
# ---------------------------------------------------------------------------
def svg_conceptual():
    w_dim, h_dim = 250, 140
    dims = [  # (tabla, x, y)
        ("dim_tiempo", 30, 20), ("dim_carrera", 375, 20), ("dim_circuito", 720, 20),
        ("dim_piloto", 30, 474), ("dim_escuderia", 375, 474), ("dim_estado", 720, 474),
    ]
    fx, fy, fw, fh = 300, 200, 400, 214
    p = [f'<svg viewBox="0 0 1000 622" xmlns="http://www.w3.org/2000/svg" class="diagrama" '
         f'font-family="Inter, sans-serif" role="img" aria-label="Modelo conceptual del DataMart">']
    # conectores
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
    # dimensiones
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
    # hecho
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
        # lado "1": dos barras junto a la dimensión
        for off in (8, 13):
            bx = x_dim + d * off
            cuerpo.append(f'<line x1="{bx}" y1="{y_pk - 6}" x2="{bx}" y2="{y_pk + 6}" stroke="#7d8aa0" stroke-width="1.6"/>')
        # lado "N": pata de gallo junto a la tabla de hechos
        bx = x_hecho - d * 12
        for dy in (-7, 0, 7):
            cuerpo.append(f'<line x1="{bx}" y1="{y_fk}" x2="{x_hecho}" y2="{y_fk + dy}" stroke="#7d8aa0" stroke-width="1.6"/>')
    for nombre, (x, y, _c) in lado.items():
        s, _h = tabla(nombre, x, y, w_dim, False)
        cuerpo += s
    s, h_fact = tabla("fact_resultado_carrera", fact_x, fact_y, w_fact, True)
    cuerpo += s
    alto = max(fact_y + h_fact, 546 + cab + 4 * fila + pie) + 20
    ancho = 880 + w_dim + 20
    return (f'<svg viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg" class="diagrama" '
            f'font-family="Inter, sans-serif" role="img" aria-label="Modelo lógico en estrella">\n'
            + "\n".join(cuerpo) + "\n</svg>")


# ---------------------------------------------------------------------------
# Tablas HTML
# ---------------------------------------------------------------------------
def diccionario(nombre):
    t = TABLAS[nombre]
    filas = []
    for col, tipo, clave, nulo, desc, origen in t["columnas"]:
        etiqueta = f'<span class="clave clave-{clave.lower()}">{clave}</span>' if clave else ""
        filas.append(
            f"<tr><td class='mono'>{html.escape(col)}</td><td class='mono'>{html.escape(tipo)}</td>"
            f"<td class='c'>{etiqueta}</td><td class='c'>{'Sí' if nulo else 'No'}</td>"
            f"<td>{html.escape(desc)}</td><td class='origen'>{html.escape(origen)}</td></tr>")
    return (f'<table class="dicc"><caption>{html.escape(t["titulo"])} (<span class="mono">{nombre}</span>)</caption>'
            "<colgroup><col style='width:27%'><col style='width:13%'><col style='width:6%'><col style='width:5%'>"
            "<col style='width:27%'><col style='width:22%'></colgroup>"
            "<thead><tr><th>Atributo</th><th>Tipo</th><th>Clave</th><th>Nulo</th><th>Descripción</th><th>Origen / regla</th></tr></thead>"
            f"<tbody>{''.join(filas)}</tbody></table>")


PALABRAS_SQL = (
    "ADD|ALTER|AND|AS|ASC|BEGIN|BETWEEN|BY|CASCADE|CASE|CHECK|COMMENT|CONSTRAINT|CREATE|DEFAULT|DELETE|DESC|"
    "DISTINCT|DROP|ELSE|END|EXISTS|FILTER|FOREIGN|FROM|GENERATED|GROUP|HAVING|IDENTITY|IF|IN|INDEX|INSERT|INTO|IS|"
    "JOIN|KEY|LIMIT|NOT|NULL|ON|OR|ORDER|OVER|PARTITION|PRIMARY|REFERENCES|ROLLBACK|SCHEMA|SELECT|SET|TABLE|THEN|"
    "TO|UNIQUE|VALUES|WHEN|WHERE|WINDOW|WITH|ALWAYS|COLUMN|LIKE|TRUE|FALSE"
)
TIPOS_SQL = "BIGINT|BOOLEAN|CHAR|DATE|INTEGER|INTERVAL|NUMERIC|SMALLINT|TIME|TIMESTAMP|VARCHAR"
_token = re.compile(
    r"(?P<com>--.*$)|(?P<str>'(?:[^']|'')*')|(?P<meta>^\\\w+.*$)|"
    rf"(?P<kw>\b(?:{PALABRAS_SQL})\b)|(?P<ty>\b(?:{TIPOS_SQL})\b)",
    re.MULTILINE,
)


def resaltar_sql(texto):
    def reemplazo(m):
        clase = m.lastgroup
        return f'<span class="sql-{clase}">{m.group(0)}</span>'
    return _token.sub(reemplazo, html.escape(texto, quote=False))


def bloque_sql(archivo):
    texto = (SQL / archivo).read_text(encoding="utf-8").rstrip()
    return f'<pre class="codigo"><code>{resaltar_sql(texto)}</code></pre>'


def extracto_sql(archivo, desde, hasta):
    """Líneas de un script entre la primera que contiene `desde` y la primera que contiene `hasta`."""
    lineas = (SQL / archivo).read_text(encoding="utf-8").splitlines()
    i = next(n for n, l in enumerate(lineas) if desde in l)
    j = next(n for n, l in enumerate(lineas[i:], start=i) if hasta in l)
    return f'<pre class="codigo"><code>{resaltar_sql(chr(10).join(lineas[i:j + 1]))}</code></pre>'


# ---------------------------------------------------------------------------
# Ensamblado
# ---------------------------------------------------------------------------
def ensamblar(numeros_pagina):
    plantilla = (BASE / "informe.html").read_text(encoding="utf-8")
    reemplazos = {
        "<!--DIAGRAMA_CONCEPTUAL-->": svg_conceptual(),
        "<!--DIAGRAMA_LOGICO-->": svg_logico(),
        "<!--EVIDENCIA_CATALOGO-->": html.escape((BASE / "evidencia" / "catalogo.txt").read_text(encoding="utf-8").rstrip()),
        "<!--EVIDENCIA_PRUEBAS-->": html.escape((BASE / "evidencia" / "pruebas_integridad.txt").read_text(encoding="utf-8").rstrip()),
    }
    for m in re.finditer(r"<!--EXTRACTO:([^|]+)\|([^|]+)\|([^>]+?)-->", plantilla):
        reemplazos[m.group(0)] = extracto_sql(m.group(1), m.group(2), m.group(3))
    for t in TABLAS:
        reemplazos[f"<!--DICC:{t}-->"] = diccionario(t)
    for archivo in sorted(p.name for p in SQL.glob("*.sql")):
        reemplazos[f"<!--SQL:{archivo}-->"] = bloque_sql(archivo)
    for clave, valor in reemplazos.items():
        if clave not in plantilla:
            sys.exit(f"Marcador no encontrado en la plantilla: {clave}")
        plantilla = plantilla.replace(clave, valor)
    # números de página del índice (data-toc="id")
    def numero(m):
        return f'{m.group(0)}{numeros_pagina.get(m.group(1), "")}'
    plantilla = re.sub(r'<span class="pag" data-toc="([\w-]+)">', numero, plantilla)
    restante = re.findall(r"<!--(?:DICC|SQL|DIAGRAMA|EVIDENCIA|EXTRACTO)[^>]*-->", plantilla)
    if restante:
        sys.exit(f"Marcadores sin reemplazar: {restante}")
    SALIDA_HTML.parent.mkdir(exist_ok=True)
    SALIDA_HTML.write_text(plantilla, encoding="utf-8")


def imprimir():
    subprocess.run(["node", str(BASE / "imprimir_pdf.js"), str(SALIDA_HTML), str(SALIDA_PDF)], check=True)


def paginas_de_titulos():
    """Busca en el PDF la página donde aparece cada título listado en el índice."""
    plantilla = (BASE / "informe.html").read_text(encoding="utf-8")
    titulos = re.findall(r'<h[12][^>]*\bid="([\w-]+)"[^>]*>(.*?)</h[12]>', plantilla, re.S)
    lector = PdfReader(str(SALIDA_PDF))
    # La extracción de texto puede perder signos de puntuación (p. ej. los dos
    # puntos de un título), así que se comparan solo letras, dígitos y espacios.
    def normalizar(t):
        return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", t)).strip()

    textos = [normalizar(pg.extract_text() or "") for pg in lector.pages]
    inicio = next(i for i, t in enumerate(textos) if "Índice" in t) + 1
    resultado = {}
    for ident, titulo in titulos:
        limpio = normalizar(html.unescape(re.sub(r"<[^>]+>", "", titulo)))
        for n in range(inicio, len(textos)):
            if limpio in textos[n]:
                resultado[ident] = n + 1
                break
        else:
            print(f"Aviso: no se encontró el título «{limpio}» en el PDF")
    return resultado


if __name__ == "__main__":
    ensamblar({})
    imprimir()
    paginas = paginas_de_titulos()
    ensamblar(paginas)
    imprimir()
    if paginas_de_titulos() != paginas:
        ensamblar(paginas_de_titulos())
        imprimir()
    print(f"PDF generado: {SALIDA_PDF} ({len(PdfReader(str(SALIDA_PDF)).pages)} páginas)")

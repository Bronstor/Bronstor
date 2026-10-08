"""Construye la primera presentación como documento Word (Arial 12) y PDF.

Uso (desde esta carpeta):
    NODE_PATH=$(npm root -g) python3 construir_docx.py

Requiere python-docx, LibreOffice (soffice) y Node.js con Playwright para
rasterizar los diagramas. Escribe ../Primera_Presentacion_DW_Formula1.docx
y ../Primera_Presentacion_DW_Formula1.pdf.
"""
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import diagramas
from modelo import TABLAS

BASE = Path(__file__).resolve().parent
SQL = BASE.parent.parent / "sql"
SALIDA_DOCX = BASE.parent / "Primera_Presentacion_DW_Formula1.docx"
ANCHO_VERTICAL = Cm(16)      # A4 con márgenes de 2,5 cm
ANCHO_HORIZONTAL = Cm(24.7)

doc = Document()


# ---------------------------------------------------------------------------
# Formato básico: todo en Arial 12, negro
# ---------------------------------------------------------------------------
def _arial(estilo, negrita=False):
    estilo.font.name = "Arial"
    estilo.font.size = Pt(12)
    estilo.font.bold = negrita
    estilo.font.italic = False
    estilo.font.color.rgb = RGBColor(0, 0, 0)
    rpr = estilo.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(atributo), "Arial")
    # Los títulos de la plantilla usan fuentes y colores "de tema" (Calibri,
    # azul) que tienen prioridad sobre lo anterior; se eliminan.
    for atributo in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(qn(atributo), None)
    color = rpr.find(qn("w:color"))
    if color is not None:
        for atributo in ("w:themeColor", "w:themeShade", "w:themeTint"):
            color.attrib.pop(qn(atributo), None)


for nombre in ("Normal", "List Bullet", "List Number", "Caption"):
    _arial(doc.styles[nombre])
for nombre in ("Heading 1", "Heading 2", "Heading 3", "Title"):
    _arial(doc.styles[nombre], negrita=True)
doc.styles["Normal"].paragraph_format.space_after = Pt(6)
doc.styles["Normal"].paragraph_format.line_spacing = 1.15
for nombre, antes in (("Heading 1", 18), ("Heading 2", 12), ("Heading 3", 8)):
    pf = doc.styles[nombre].paragraph_format
    pf.space_before, pf.space_after, pf.keep_with_next = Pt(antes), Pt(6), True

for seccion in doc.sections:
    seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
    seccion.left_margin = seccion.right_margin = Cm(2.5)
    seccion.top_margin = seccion.bottom_margin = Cm(2.5)


# ---------------------------------------------------------------------------
# Ayudantes de contenido
# ---------------------------------------------------------------------------
def _runs(parrafo, texto):
    """Agrega el texto al párrafo; **así** se vuelve negrita."""
    for i, trozo in enumerate(texto.split("**")):
        if trozo:
            parrafo.add_run(trozo).bold = bool(i % 2)


def h1(texto):
    doc.add_heading(texto.upper(), level=1)


def h2(texto):
    doc.add_heading(texto, level=2)


def h3(texto):
    doc.add_heading(texto, level=3)


def p(texto, alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY):
    parrafo = doc.add_paragraph()
    parrafo.alignment = alineacion
    _runs(parrafo, texto)
    return parrafo


def lista(elementos, numerada=False):
    for e in elementos:
        parrafo = doc.add_paragraph(style="List Number" if numerada else "List Bullet")
        parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _runs(parrafo, e)


def nota(texto):
    """Párrafo con sangría para destacar una definición (sin colores)."""
    parrafo = doc.add_paragraph()
    parrafo.paragraph_format.left_indent = Cm(1)
    parrafo.paragraph_format.right_indent = Cm(1)
    _runs(parrafo, texto)


def _set_celda(celda, texto, negrita=False, centrado=False):
    celda.text = ""
    parrafo = celda.paragraphs[0]
    parrafo.paragraph_format.space_after = Pt(0)
    parrafo.paragraph_format.line_spacing = 1.0
    if centrado:
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if negrita:
        parrafo.add_run(str(texto)).bold = True
    else:
        _runs(parrafo, str(texto))


def tabla(encabezados, filas, anchos, titulo=None, centradas=(), ancho_total=None):
    """Tabla con bordes. `anchos` son proporciones por columna."""
    ancho_total = ancho_total or ANCHO_VERTICAL
    if titulo:
        parrafo = doc.add_paragraph()
        parrafo.paragraph_format.space_after = Pt(2)
        parrafo.paragraph_format.keep_with_next = True
        parrafo.add_run(titulo).bold = True
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    total = sum(anchos)
    for j, enc in enumerate(encabezados):
        _set_celda(t.rows[0].cells[j], enc, negrita=True, centrado=True)
    # fila de encabezado repetida en cada página
    trpr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trpr.append(th)
    for fila in filas:
        celdas = t.add_row().cells
        for j, valor in enumerate(fila):
            _set_celda(celdas[j], valor, centrado=(j in centradas))
    juntar = len(filas) <= 10  # las tablas cortas no se parten entre páginas
    for i, fila in enumerate(t.rows):
        trpr = fila._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        cs.set(qn("w:val"), "true")
        trpr.append(cs)
        for j, celda in enumerate(fila.cells):
            celda.width = int(ancho_total * anchos[j] / total)
            if juntar and i < len(t.rows) - 1:
                for parrafo in celda.paragraphs:
                    parrafo.paragraph_format.keep_with_next = True
    # LibreOffice y Word toman el ancho de las columnas de w:gridCol
    for j, columna in enumerate(t.columns):
        columna.width = int(ancho_total * anchos[j] / total)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def figura(ruta, ancho, leyenda):
    parrafo = doc.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.paragraph_format.keep_with_next = True
    parrafo.add_run().add_picture(str(ruta), width=ancho)
    pie = doc.add_paragraph()
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _runs(pie, leyenda)


def codigo(archivo):
    """Inserta un script SQL línea por línea (misma fuente Arial 12)."""
    texto = (SQL / archivo).read_text(encoding="utf-8").rstrip()
    for linea in texto.splitlines():
        parrafo = doc.add_paragraph()
        parrafo.paragraph_format.space_after = Pt(0)
        parrafo.paragraph_format.line_spacing = 1.0
        parrafo.paragraph_format.left_indent = Cm(0.5)
        sangria = len(linea) - len(linea.lstrip(" "))
        parrafo.paragraph_format.first_line_indent = Cm(0.25 * sangria)
        parrafo.add_run(linea.strip(" ") if linea.strip() else "")
    doc.add_paragraph()


def extracto(archivo, desde, hasta):
    lineas = (SQL / archivo).read_text(encoding="utf-8").splitlines()
    i = next(n for n, l in enumerate(lineas) if desde in l)
    j = next(n for n, l in enumerate(lineas[i:], start=i) if hasta in l)
    for linea in lineas[i:j + 1]:
        parrafo = doc.add_paragraph()
        parrafo.paragraph_format.space_after = Pt(0)
        parrafo.paragraph_format.line_spacing = 1.0
        parrafo.paragraph_format.left_indent = Cm(0.5)
        sangria = len(linea) - len(linea.lstrip(" "))
        parrafo.paragraph_format.first_line_indent = Cm(0.25 * sangria)
        parrafo.add_run(linea.strip(" "))
    doc.add_paragraph()


def diccionario(nombre, ancho_total):
    t = TABLAS[nombre]
    filas = [(col, tipo, clave or "—", "Sí" if nulo else "No", desc, origen)
             for col, tipo, clave, nulo, desc, origen in t["columnas"]]
    tabla(["Atributo", "Tipo de dato", "Clave", "Nulo", "Descripción", "Origen / regla ETL"],
          filas, [21, 14, 7, 6, 30, 22], titulo=f'{t["titulo"]} ({nombre})',
          centradas=(2, 3), ancho_total=ancho_total)


def seccion_horizontal():
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Cm(29.7), Cm(21)
    return s


def seccion_vertical():
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.PORTRAIT
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    return s


def leer_evidencia():
    """Lee los bloques de salida de psql guardados en evidencia/catalogo.txt."""
    bloques = []
    for bloque in (BASE / "evidencia" / "catalogo.txt").read_text(encoding="utf-8").split("\n\n"):
        lineas = [l for l in bloque.splitlines() if "|" in l and not set(l.strip()) <= set("-+")]
        if lineas:
            bloques.append([[c.strip() for c in l.split("|")] for l in lineas])
    return bloques


def leer_pruebas():
    texto = (BASE / "evidencia" / "pruebas_integridad.txt").read_text(encoding="utf-8")
    pruebas = re.findall(r"--- (Prueba \d+): (.*?) -> debe fallar\n.*?ERROR:\s+(.*?)\n", texto)
    return [(num, desc, error.strip()) for num, desc, error in pruebas]


# ===========================================================================
# CARÁTULA
# ===========================================================================
for texto, negrita in (
    ("[NOMBRE DE LA UNIVERSIDAD]", True), ("[Facultad]", True), ("[Carrera]", True), ("", False), ("", False),
    ("BASE DE DATOS III", True), ("Proyecto Base de Datos 3: Implementación de un Data Warehouse", False),
    ("", False), ("", False),
    ("DATA WAREHOUSE DEL CAMPEONATO MUNDIAL DE FÓRMULA 1", True),
    ("DataMart de Rendimiento en Carrera (temporadas 1950–2024)", False), ("", False),
    ("Primera Presentación (desde el punto 1 hasta el punto 5)", True), ("", False), ("", False), ("", False),
    ("Docente: Rodnie Montaño Aguilera", False), ("", False),
    ("Integrantes:", False), ("Jhonatan Moisés Villca", False), ("[Integrante 2]", False), ("[Integrante 3]", False),
    ("", False), ("Semestre II/2026", False), ("Octubre de 2026", False),
):
    parrafo = doc.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.add_run(texto).bold = negrita
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ===========================================================================
# 1. TEMA DEL PROYECTO
# ===========================================================================
h1("1. Tema del Proyecto")

h2("1.1 Tema de interés seleccionado a partir de un conjunto de datos público (Kaggle)")
nota("**Tema:** Análisis histórico del rendimiento competitivo de pilotos, escuderías y circuitos en el Campeonato Mundial de Fórmula 1, temporadas 1950 a 2024.")
p("La Fórmula 1 es la máxima categoría del automovilismo de monoplazas y está regulada por la Federación Internacional del Automóvil (FIA). Cada temporada se compone de una serie de Grandes Premios (siete en 1950 y veinticuatro en 2024) que se disputan en circuitos de distintos países. En cada carrera los pilotos compiten representando a una escudería (constructor) y, según su posición final, reciben puntos que se acumulan en dos campeonatos: el de Pilotos y el de Constructores.")
p("El conjunto de datos es público y se obtuvo de Kaggle, como recomienda la consigna:")
tabla(["Característica", "Detalle"], [
    ("Nombre", "Formula 1 World Championship (1950 – 2024)"),
    ("Publicado por", "Rohan Rao, en Kaggle"),
    ("Dirección", "https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020"),
    ("Origen de los datos", "Ergast Developer API, base de datos histórica de resultados de la Fórmula 1"),
    ("Formato", "14 archivos CSV relacionados mediante identificadores numéricos (modelo relacional normalizado)"),
    ("Cobertura", "Temporadas 1950 a 2024 (aproximadamente 1 125 Grandes Premios)"),
    ("Valores nulos", "Representados con la cadena \\N"),
], [30, 70], titulo="Ficha del conjunto de datos")

h2("1.2 El conjunto de datos contiene información suficiente para plantear objetivos de análisis, aplicar modelado dimensional y construir un Data Warehouse")
p("El conjunto de datos reúne catorce archivos que describen setenta y cinco temporadas. La siguiente tabla resume su contenido y el uso que se le da en el proyecto:")
tabla(["Archivo", "Contenido", "Registros (aprox.)", "Uso en el proyecto"], [
    ("races.csv", "Carreras: temporada, ronda, circuito, nombre, fecha y hora", "1 125", "dim_carrera, dim_tiempo"),
    ("results.csv", "Resultado de cada piloto en cada carrera: grilla, posición, puntos, vueltas, tiempos, estado", "26 700", "Tabla de hechos"),
    ("drivers.csv", "Pilotos: nombre, código, número, fecha de nacimiento, nacionalidad", "860", "dim_piloto"),
    ("constructors.csv", "Escuderías y su nacionalidad", "210", "dim_escuderia"),
    ("circuits.csv", "Circuitos: nombre, localidad, país, coordenadas y altitud", "77", "dim_circuito"),
    ("status.csv", "Catálogo de estados de finalización (Finished, Engine, Accident, etc.)", "139", "dim_estado"),
    ("driver_standings.csv", "Puntos y posición de cada piloto en el campeonato tras cada carrera", "34 800", "Métricas de campeonato"),
    ("sprint_results.csv", "Resultados de las carreras sprint (desde 2021)", "360", "dim_carrera (tiene_sprint)"),
    ("seasons.csv", "Temporadas y enlace de referencia", "75", "Cubierto por dim_tiempo"),
    ("qualifying.csv", "Clasificación: posición y tiempos en Q1, Q2 y Q3", "10 500", "DataMart 3 (propuesto)"),
    ("lap_times.csv", "Tiempo y posición de cada piloto en cada vuelta (desde 1996)", "589 000", "DataMart 2 (propuesto)"),
    ("pit_stops.csv", "Paradas en boxes: vuelta y duración (desde 2011)", "11 400", "DataMart 2 (propuesto)"),
    ("constructor_results.csv", "Puntos de cada escudería en cada carrera", "12 600", "DataMart 3 (propuesto)"),
    ("constructor_standings.csv", "Puntos y posición de cada escudería en el campeonato tras cada carrera", "13 400", "DataMart 3 (propuesto)"),
], [24, 38, 15, 23], titulo="Archivos del conjunto de datos", centradas=(2,))
p("Las cantidades de registros son aproximadas para la versión 1950–2024 del dataset y se confirmarán durante la extracción del proceso ETL.")
p("Esta información es suficiente para los tres fines que exige la consigna:")
tabla(["Requisito", "Lo que aporta el conjunto de datos"], [
    ("Plantear objetivos de análisis", "Métricas numéricas por evento (posiciones, puntos, vueltas, tiempos, velocidad) y estados de finalización que permiten medir victorias, podios, abandonos, dominio y ritmo (punto 2)."),
    ("Aplicar modelado dimensional", "Eventos medibles para las tablas de hechos (results, lap_times, pit_stops, qualifying, standings) y entidades descriptivas para las dimensiones (pilotos, escuderías, circuitos, carreras, estados), con jerarquías naturales: década → año, continente → país → circuito, categoría → estado."),
    ("Construir un Data Warehouse", "Varios procesos de negocio que dan lugar a tres DataMarts con dimensiones compartidas (punto 3); historia de 75 años para el análisis temporal; volumen suficiente (≈ 27 000 resultados y ≈ 589 000 vueltas); y datos que requieren limpieza e integración, lo que justifica el proceso ETL."),
], [30, 70], titulo="Suficiencia del conjunto de datos")
h3("Consideraciones de calidad de los datos")
p("La revisión de la estructura del dataset permitió identificar aspectos que se consideraron en el diseño y que se resolverán en el proceso ETL:")
tabla(["Hallazgo", "Ejemplo", "Tratamiento en el diseño / ETL"], [
    ("Nulos codificados como texto", "\\N en position, code, time", "Conversión a NULL; las columnas que lo admiten se declaran como nulas"),
    ("Tiempos almacenados como texto", "fastestLapTime = \"1:27.452\"", "Conversión a milisegundos (INTEGER) para poder promediar y comparar"),
    ("Datos que existen solo en ciertas épocas", "Vuelta rápida desde 2004, tiempos por vuelta desde 1996, paradas desde 2011", "Se mantienen nulos; la cobertura se indica en los reportes"),
    ("Más de un resultado por piloto en una carrera", "Autos compartidos en los años cincuenta", "El grano se define por resultado (resultId), no por piloto y carrera"),
    ("Puntos fraccionarios", "Medios puntos en carreras acortadas (p. ej. Bélgica 2021)", "Tipo NUMERIC(5,2)"),
    ("Cambios del sistema de puntuación", "9 puntos por victoria (1961–1990) frente a 25 (desde 2010)", "Métrica adicional puntos_sistema_actual"),
    ("Códigos de resultado en texto", "R, D, E, W, F, N en positionText", "Indicadores es_abandono y es_finalizado"),
    ("Estados muy detallados", "139 estados distintos (Engine, Gearbox, Collision, etc.)", "Agrupación en categorías de análisis en dim_estado"),
    ("500 Millas de Indianápolis (1950–1960)", "Pilotos que solo corrieron esa prueba puntuable", "Se conservan; se identifican por el nombre del Gran Premio"),
], [30, 33, 37], titulo="Hallazgos de calidad y tratamiento previsto")

h2("1.3 Contexto de los datos: qué información representan y qué necesidad de análisis se desea resolver")
h3("Qué información representan los datos")
p("Los datos registran la historia oficial del campeonato. Para explicarlos es necesario conocer los conceptos del dominio que aparecen en los archivos:")
tabla(["Concepto", "Significado en los datos"], [
    ("Temporada y ronda", "Cada año es una temporada del campeonato; la ronda indica el orden de cada Gran Premio dentro de ella (races.year, races.round)."),
    ("Gran Premio y circuito", "Un Gran Premio es una carrera puntuable que se disputa en un circuito. Un mismo circuito puede albergar Grandes Premios con distintos nombres a lo largo de la historia."),
    ("Piloto y escudería", "El piloto conduce un auto de una escudería. Un piloto puede cambiar de escudería entre temporadas e incluso durante una misma temporada; en los primeros años varios pilotos compartían un mismo auto."),
    ("Grilla de salida", "Posición desde la que larga el piloto (grid). El valor 0 indica que largó desde los boxes o que no tiene posición asignada."),
    ("Resultado", "Posición final clasificada (position) u otro código (positionText): R = retirado, D = descalificado, E = excluido, W = retirado antes de largar, F = no clasificó a la carrera, N = no clasificado."),
    ("Estado", "Motivo con el que terminó la carrera: Finished, +1 Lap, Engine, Accident, Collision, etc. (status.csv)."),
    ("Puntos", "Se otorgan según la posición final. El sistema de puntuación cambió varias veces (por ejemplo, 9 puntos por victoria entre 1961 y 1990 y 25 desde 2010), por lo que los puntos de distintas épocas no son directamente comparables."),
    ("Campeonato", "Suma de puntos de la temporada. driver_standings.csv registra los puntos y la posición acumulados de cada piloto después de cada carrera."),
], [25, 75], titulo="Conceptos del dominio")
h3("Qué necesidad de análisis se desea resolver")
p("Los datos están organizados en un modelo relacional normalizado de catorce tablas, adecuado para registrar resultados pero no para el análisis histórico. Preguntas como «¿qué escudería dominó cada década?», «¿en qué circuitos es más determinante largar desde la pole?» o «¿qué pilotos fueron más efectivos si se comparan épocas con el mismo sistema de puntos?» exigen unir varias tablas, interpretar códigos, convertir tiempos almacenados como texto y tratar distintos sistemas de puntuación en cada consulta.")
nota("**Necesidad de análisis:** evaluar de forma consistente y comparable en el tiempo el rendimiento de pilotos, escuderías y circuitos: quién gana, con qué frecuencia, con qué confiabilidad y bajo qué condiciones.")
p("Los usuarios que se benefician de este análisis son:")
lista([
    "**Equipos (escuderías):** confiabilidad mecánica, conversión de la posición de salida en resultado y comparación con sus rivales.",
    "**Analistas deportivos y medios:** comparaciones históricas entre pilotos y épocas, dominio de escuderías y evolución del campeonato.",
    "**Patrocinadores:** pilotos y escuderías con mayor frecuencia de victorias, podios y puntos.",
    "**Organizadores de Grandes Premios:** circuitos con más adelantamientos y menor dependencia de la posición de salida.",
])

h2("1.4 Justificación de la temática (problema analítico diferenciado)")
p("La consigna no acepta temáticas excesivamente comunes o repetitivas (supermercados, hoteles, comercio electrónico, logs de servidores, bibliotecas, restaurantes o sistemas genéricos de inventario y ventas). El tema elegido no pertenece a ninguna de ellas y plantea un problema analítico claramente diferenciado, con complejidad suficiente para justificar un Data Warehouse:")
lista([
    "**No es un proceso de compra y venta.** El hecho central es un resultado deportivo con métricas de naturaleza diversa: ordinales (posiciones), aditivas (puntos, vueltas), semiaditivas (puntos acumulados del campeonato) y temporales (tiempos de vuelta).",
    "**Profundidad histórica.** Setenta y cinco temporadas con cambios de reglamento obligan a normalizar los puntos para comparar épocas y a manejar datos que solo existen en ciertos periodos.",
    "**Varios procesos y granularidades.** Resultados, clasificación, vueltas, paradas en boxes y campeonatos permiten proponer tres DataMarts con dimensiones conformadas.",
    "**Calidad de datos no trivial.** Nulos codificados como texto, tiempos en formato «m:ss.mmm», pilotos con más de un resultado en la misma carrera y medios puntos en carreras acortadas.",
])

# ===========================================================================
# 2. OBJETIVOS
# ===========================================================================
h1("2. Objetivos del Data Warehouse")

h2("2.1 Objetivo general")
nota("Diseñar e implementar un Data Warehouse para el Campeonato Mundial de Fórmula 1, comenzando por el DataMart de Rendimiento en Carrera, que integre y depure los resultados históricos de cada Gran Premio (1950–2024) para analizar el rendimiento de pilotos, escuderías y circuitos mediante indicadores, consultas analíticas, cubos OLAP, reportes y cuadros de mando que apoyen la toma de decisiones deportivas y comerciales.")

h2("2.2 Objetivos específicos")
p("Los objetivos específicos están orientados al análisis de los datos disponibles. Cada uno es medible y puede responderse mediante indicadores, métricas, reportes o consultas analíticas, como se detalla después de la tabla.")
tabla(["Código", "Objetivo específico", "Pregunta de negocio"], [
    ("OE1", "Medir la conversión de la posición de salida en resultado final, calculando el porcentaje de victorias obtenidas desde la pole position y el promedio de posiciones ganadas por temporada, circuito y escudería.", "¿Cuán determinante es largar primero? ¿Qué escuderías remontan más?"),
    ("OE2", "Determinar el nivel de dominio de las escuderías por temporada y por década mediante su participación porcentual en las victorias, los podios y los puntos.", "¿Qué escudería dominó cada época y con qué margen?"),
    ("OE3", "Cuantificar la confiabilidad de las escuderías mediante la tasa de abandono y la tasa de finalización por temporada y circuito, identificando las categorías de causa más frecuentes.", "¿Qué equipos abandonan más y por qué motivo?"),
    ("OE4", "Comparar el rendimiento histórico de los pilotos mediante los puntos por carrera normalizados al sistema actual, las tasas de victoria y de podio y la edad promedio al ganar, y seguir su evolución en el campeonato ronda a ronda.", "¿Quiénes fueron los pilotos más efectivos, comparando épocas de forma justa?"),
    ("OE5", "Caracterizar los circuitos y países sede según la cantidad de Grandes Premios disputados, el índice de adelantamiento, la tasa de abandono y el porcentaje de victorias desde la pole.", "¿En qué circuitos es más difícil adelantar o más frecuente abandonar?"),
    ("OE6", "Evaluar la evolución del ritmo de carrera por circuito y temporada, desde 2004, mediante el tiempo y la velocidad media de la vuelta más rápida y su variación porcentual interanual.", "¿Los autos son cada año más rápidos en cada circuito?"),
], [10, 58, 32], titulo="Objetivos específicos", centradas=(0,))
h3("Medición de los objetivos: indicadores, métricas, reportes y consultas")
p("Cada objetivo se mide con indicadores (KPI) calculados a partir de las métricas de la tabla de hechos. La última columna indica el reporte (R) o cuadro de mando (CM) previsto para presentarlo; además, cada objetivo tiene su consulta analítica SQL en el Anexo B. Las tasas y porcentajes se recalculan siempre desde sus componentes aditivos, nunca promediando porcentajes.")
tabla(["OE", "Indicador", "Fórmula (métricas del DataMart)", "Tipo", "Se responde en"], [
    ("OE1", "% de conversión de la pole", "Σ(es_victoria × es_pole) / Σ es_pole × 100", "Porcentaje", "R1, CM2"),
    ("OE1", "Promedio de posiciones ganadas", "AVG(posiciones_ganadas)", "Promedio", "R1"),
    ("OE2", "% de victorias en la temporada", "Σ es_victoria (escudería) / Σ es_victoria (temporada) × 100", "Porcentaje", "R2, CM1"),
    ("OE2", "% de podios en la temporada", "Σ es_podio (escudería) / Σ es_podio (temporada) × 100", "Porcentaje", "R2"),
    ("OE2", "Cuota de puntos", "Σ puntos (escudería) / Σ puntos (temporada) × 100", "Porcentaje", "R2, CM1"),
    ("OE3", "Tasa de abandono", "Σ es_abandono / N.º participaciones × 100", "Porcentaje", "R3, CM1"),
    ("OE3", "Tasa de finalización", "Σ es_finalizado / N.º participaciones × 100", "Porcentaje", "R3, CM1"),
    ("OE3", "Distribución de causas de abandono", "Abandonos por categoría de estado / total de abandonos × 100", "Porcentaje", "R3"),
    ("OE4", "Puntos normalizados por carrera", "Σ puntos_sistema_actual / N.º participaciones", "Promedio", "R4, CM2"),
    ("OE4", "Tasa de victorias y de podios", "Σ es_victoria (o es_podio) / N.º participaciones × 100", "Porcentaje", "R4, CM2"),
    ("OE4", "Edad promedio al ganar", "AVG(edad_piloto) donde es_victoria = 1", "Promedio", "R4"),
    ("OE4", "Evolución en el campeonato", "puntos_acumulados_temporada y posicion_campeonato por ronda", "Último valor", "R4"),
    ("OE5", "Grandes Premios disputados", "COUNT(DISTINCT carrera) por circuito", "Conteo", "R5"),
    ("OE5", "Índice de adelantamiento", "AVG(posiciones_ganadas) por circuito", "Promedio", "R5, CM2"),
    ("OE5", "Tasa de abandono y % de victorias desde la pole por circuito", "Iguales a OE3 y OE1, agrupados por circuito", "Porcentaje", "R5"),
    ("OE6", "Mejor vuelta del Gran Premio", "MIN(tiempo_vuelta_rapida_ms)", "Mínimo", "R5"),
    ("OE6", "Velocidad media de vuelta rápida", "AVG(velocidad_vuelta_rapida_kmh)", "Promedio", "R5, CM2"),
    ("OE6", "Variación interanual del ritmo", "(velocidad año t − velocidad año t−1) / velocidad año t−1 × 100", "Porcentaje", "R5"),
], [8, 25, 36, 16, 15], titulo="Indicadores de cada objetivo", centradas=(0, 4))

h2("2.3 Los objetivos como base para definir hechos, dimensiones, métricas, granularidad, reportes y cuadros de mando")
p("Los objetivos específicos son la base del diseño. La siguiente tabla muestra qué elemento del DataMart se deriva de cada objetivo:")
tabla(["OE", "Hecho y granularidad", "Dimensiones (nivel de análisis)", "Métricas", "Reporte", "Cuadro de mando"], [
    ("OE1", "Resultado de carrera: piloto-auto-Gran Premio", "Carrera (temporada), Circuito, Escudería", "es_pole, es_victoria, posiciones_ganadas", "R1", "CM2"),
    ("OE2", "Resultado de carrera: piloto-auto-Gran Premio", "Carrera (temporada), Tiempo (década), Escudería", "es_victoria, es_podio, puntos", "R2", "CM1"),
    ("OE3", "Resultado de carrera: piloto-auto-Gran Premio", "Escudería, Carrera (temporada), Circuito, Estado (categoría)", "es_abandono, es_finalizado", "R3", "CM1"),
    ("OE4", "Resultado de carrera: piloto-auto-Gran Premio", "Piloto, Carrera (temporada, ronda)", "puntos_sistema_actual, es_victoria, es_podio, edad_piloto, puntos_acumulados_temporada, posicion_campeonato", "R4", "CM2"),
    ("OE5", "Resultado de carrera: piloto-auto-Gran Premio", "Circuito (continente, país, circuito)", "posiciones_ganadas, es_abandono, es_pole, es_victoria", "R5", "CM2"),
    ("OE6", "Resultado de carrera: piloto-auto-Gran Premio", "Circuito, Carrera (temporada)", "tiempo_vuelta_rapida_ms, velocidad_vuelta_rapida_kmh", "R5", "CM2"),
], [8, 22, 24, 28, 9, 9], titulo="Elementos del diseño que se derivan de cada objetivo", centradas=(0, 4, 5))
p("Como todos los objetivos se responden agregando resultados individuales (por temporada, escudería, piloto o circuito), la granularidad del hecho debe ser la más detallada disponible: el resultado de un piloto con un auto en un Gran Premio (punto 3.4). A partir de los objetivos se prevén los siguientes reportes y cuadros de mando, que se construirán en la segunda presentación:")
tabla(["Código", "Nombre", "Contenido previsto", "Objetivos"], [
    ("R1", "Conversión de la posición de salida", "Evolución del % de victorias desde la pole por temporada; posiciones ganadas por escudería y circuito.", "OE1"),
    ("R2", "Dominio de escuderías", "Participación en victorias, podios y puntos por escudería, temporada y década.", "OE2"),
    ("R3", "Confiabilidad y causas de abandono", "Tasas de abandono y de finalización por escudería y temporada; distribución por categoría de causa.", "OE3"),
    ("R4", "Ranking histórico de pilotos", "Puntos normalizados por carrera, tasas de victoria y podio, edad al ganar y evolución del campeonato ronda a ronda.", "OE4"),
    ("R5", "Circuitos y ritmo de carrera", "Grandes Premios, índice de adelantamiento y tasa de abandono por circuito; evolución de la vuelta rápida.", "OE5, OE6"),
    ("CM1", "Cuadro de mando de escuderías", "KPI: % de victorias, cuota de puntos, tasa de abandono y de finalización. Filtros: década, temporada, escudería.", "OE2, OE3"),
    ("CM2", "Cuadro de mando de pilotos y circuitos", "KPI: puntos normalizados por carrera, tasa de victorias, % de conversión de la pole, índice de adelantamiento, velocidad de vuelta rápida. Filtros: piloto, país, circuito, temporada.", "OE1, OE4, OE5, OE6"),
], [10, 26, 48, 16], titulo="Reportes y cuadros de mando previstos", centradas=(0,))

# ===========================================================================
# 3. MODELADO CONCEPTUAL
# ===========================================================================
h1("3. Modelado Conceptual del DataMart")

h2("3.1 Tres posibles DataMarts relacionados con el tema")
p("Siguiendo la metodología dimensional de Kimball, primero se identificaron los procesos de negocio que generan eventos medibles en las fuentes de datos:")
tabla(["Proceso de negocio", "Evento que se registra", "Fuente", "Cobertura"], [
    ("Resultado de carrera", "Posición, puntos, vueltas y estado final de cada piloto en un Gran Premio", "results, races", "1950–2024"),
    ("Clasificación", "Tiempos de las sesiones Q1, Q2 y Q3 que definen la grilla", "qualifying", "Completa desde 2003"),
    ("Vueltas en carrera", "Tiempo y posición de cada piloto en cada vuelta", "lap_times", "1996–2024"),
    ("Paradas en boxes", "Vuelta y duración de cada parada", "pit_stops", "2011–2024"),
    ("Campeonato de pilotos", "Puntos, posición y victorias acumulados tras cada ronda", "driver_standings", "1950–2024"),
    ("Campeonato de constructores", "Puntos y posición de cada escudería tras cada ronda", "constructor_standings, constructor_results", "1958–2024"),
], [24, 38, 22, 16], titulo="Procesos de negocio presentes en el conjunto de datos")
p("Con estos procesos se identificaron tres posibles DataMarts relacionados con el tema:")
h3("DataMart 1: Rendimiento en Carrera")
lista([
    "**Procesos:** resultado de carrera; el campeonato de pilotos se incorpora como métrica acumulada.",
    "**Hecho y grano:** fact_resultado_carrera, un registro por resultado de un piloto con un auto en un Gran Premio (≈ 26 700 registros).",
    "**Dimensiones:** Tiempo, Carrera, Circuito, Piloto, Escudería, Estado.",
    "**Métricas:** puntos, posiciones, posiciones ganadas, vueltas, tiempos, vuelta rápida, edad; indicadores de victoria, podio, pole y abandono; puntos acumulados.",
    "**Usuarios:** analistas deportivos, equipos, medios y patrocinadores.",
    "**Cobertura:** completa, 1950–2024.",
])
h3("DataMart 2: Estrategia en Pista")
lista([
    "**Procesos:** vueltas en carrera y paradas en boxes.",
    "**Hechos y grano:** fact_vuelta, un registro por vuelta de un piloto en una carrera (≈ 589 000); fact_parada_boxes, un registro por parada de un piloto en una carrera (≈ 11 400).",
    "**Dimensiones:** Tiempo, Carrera, Circuito, Piloto, Escudería (derivada del resultado del piloto en esa carrera).",
    "**Métricas:** tiempo de vuelta, posición en cada vuelta, duración de la parada, vuelta de la parada.",
    "**Usuarios:** ingenieros de estrategia de los equipos.",
    "**Limitación:** solo desde 1996 (vueltas) y 2011 (paradas).",
])
h3("DataMart 3: Clasificación y Campeonato")
lista([
    "**Procesos:** clasificación y campeonatos de pilotos y de constructores.",
    "**Hechos y grano:** fact_clasificacion, un registro por piloto en la clasificación de un Gran Premio; fact_posicion_campeonato, instantánea periódica con los puntos y la posición de cada piloto o escudería tras cada ronda.",
    "**Dimensiones:** Tiempo, Carrera, Circuito, Piloto, Escudería.",
    "**Métricas:** tiempos Q1 a Q3 y posición de clasificación (no aditivas); puntos y victorias acumulados (semiaditivas).",
    "**Usuarios:** medios, aficionados y organizadores.",
    "**Limitación:** clasificación completa solo desde 2003.",
])
p("La matriz de bus relaciona cada proceso de negocio con las dimensiones que lo describen. Las dimensiones compartidas se diseñan una sola vez (dimensiones conformadas) para que los tres DataMarts puedan integrarse en un mismo Data Warehouse.")
tabla(["Proceso de negocio", "Tiempo", "Carrera", "Circuito", "Piloto", "Escudería", "Estado", "DataMart"], [
    ("Resultado de carrera", "X", "X", "X", "X", "X", "X", "1"),
    ("Vueltas en carrera", "X", "X", "X", "X", "X*", "", "2"),
    ("Paradas en boxes", "X", "X", "X", "X", "X*", "", "2"),
    ("Clasificación", "X", "X", "X", "X", "X", "", "3"),
    ("Campeonato de pilotos", "X", "X", "X", "X", "", "", "3 (y métrica en 1)"),
    ("Campeonato de constructores", "X", "X", "X", "", "X", "", "3"),
], [26, 9, 9, 10, 9, 11, 9, 17], titulo="Matriz de bus del Data Warehouse", centradas=(1, 2, 3, 4, 5, 6, 7))
p("* La escudería no está en el archivo de origen; se obtiene del resultado del mismo piloto en la misma carrera.")

h2("3.2 Selección del DataMart que aporta mayor valor al contexto de negocio")
p("De los tres DataMarts propuestos se seleccionó el que aporta mayor valor al contexto de negocio definido en el punto 1.3. Para ello se evaluaron con criterios ponderados (puntaje de 1 a 5):")
tabla(["Criterio", "Peso", "DM1 Rendimiento", "DM2 Estrategia", "DM3 Clasificación"], [
    ("Alineación con los objetivos del proyecto", "30 %", "5", "2", "3"),
    ("Cobertura histórica de los datos", "25 %", "5", "2", "4"),
    ("Disponibilidad y calidad de los datos", "20 %", "4", "3", "4"),
    ("Valor para los usuarios del negocio", "15 %", "5", "4", "4"),
    ("Viabilidad del ETL y de los cubos OLAP", "10 %", "5", "3", "4"),
    ("**Puntaje ponderado**", "**100 %**", "**4,80**", "**2,60**", "**3,70**"),
], [40, 12, 16, 16, 16], titulo="Matriz de evaluación de los DataMarts", centradas=(1, 2, 3, 4))
p("**DataMart seleccionado: DataMart 1, Rendimiento en Carrera**, por las siguientes razones:")
lista([
    "El resultado de carrera es el proceso central del deporte: de él derivan los puntos, las victorias y los campeonatos.",
    "Es el único proceso con cobertura completa de 1950 a 2024, lo que permite el análisis histórico entre épocas.",
    "Permite responder los seis objetivos específicos planteados.",
    "Sus dimensiones (Tiempo, Carrera, Circuito, Piloto, Escudería) son las dimensiones conformadas que reutilizarán los DataMarts 2 y 3.",
    "Su volumen es manejable para la carga con Apache Hop y presenta suficientes problemas de calidad y transformación para justificar el proceso ETL.",
], numerada=True)

h2("3.3 Modelo conceptual del DataMart: procesos de negocio, hechos y dimensiones")
p("**Proceso de negocio principal:** la disputa de un Gran Premio, concretamente el resultado oficial que obtiene cada participante (archivo results). Como proceso complementario se incorpora el campeonato de pilotos (driver_standings), del que se toman los puntos y la posición acumulados después de cada carrera.")
p("**Hecho:** Resultado de carrera. **Dimensiones:** seis, que responden a las preguntas cuándo (Tiempo), qué evento (Carrera), dónde (Circuito), quién (Piloto), con qué equipo (Escudería) y cómo terminó (Estado). Son las necesarias para cumplir los objetivos, según la tabla del punto 2.3.")
figura(diagramas.exportar_png(BASE / "build")["conceptual"], Cm(16),
       "**Figura 1.** Modelo conceptual del DataMart Rendimiento en Carrera: hecho central, dimensiones y jerarquías.")
tabla(["Elemento", "Tipo", "Descripción", "Objetivos"], [
    ("Resultado de carrera", "Hecho", "Desempeño de un piloto en un Gran Premio: posiciones, puntos, vueltas, tiempos e indicadores de victoria, podio, pole y abandono.", "OE1 a OE6"),
    ("Tiempo", "Dimensión", "Fecha de la carrera con su jerarquía de calendario hasta la década.", "OE2"),
    ("Carrera", "Dimensión", "El Gran Premio: temporada, ronda, nombre, carrera sprint y sistema de puntuación vigente.", "OE1 a OE4, OE6"),
    ("Circuito", "Dimensión", "Lugar de la carrera, con su jerarquía geográfica (continente, país, localidad).", "OE1, OE3, OE5, OE6"),
    ("Piloto", "Dimensión", "Datos personales y deportivos del piloto.", "OE4"),
    ("Escudería", "Dimensión", "Equipo o constructor con el que corrió el piloto.", "OE1, OE2, OE3"),
    ("Estado", "Dimensión", "Forma en que terminó la carrera, agrupada en categorías (finalizó, falla mecánica, accidente, etc.).", "OE3"),
], [20, 14, 48, 18], titulo="Elementos del modelo conceptual")
h3("Jerarquías de las dimensiones")
p("Las jerarquías permiten navegar desde niveles agregados hacia el detalle (drill-down) y servirán como niveles de los cubos OLAP.")
tabla(["Dimensión", "Jerarquía (de lo general al detalle)", "Uso en el análisis"], [
    ("Tiempo", "Década → Año → Semestre → Trimestre → Mes → Fecha", "Evolución histórica y comparación de épocas"),
    ("Carrera", "Temporada → Gran Premio (ronda)", "Rendimiento por temporada y evolución ronda a ronda"),
    ("Circuito", "Continente → País → Localidad → Circuito", "Análisis geográfico y efecto del circuito"),
    ("Piloto", "Nacionalidad → Piloto", "Rankings de pilotos y de países"),
    ("Escudería", "Nacionalidad → Escudería", "Dominio de equipos"),
    ("Estado", "Categoría → Estado", "Causas de abandono"),
], [18, 44, 38], titulo="Jerarquías definidas")

h2("3.4 Granularidad de cada hecho: qué representa cada registro de la tabla de hechos")
p("El DataMart seleccionado tiene una tabla de hechos, fact_resultado_carrera. Su granularidad es la siguiente:")
nota("**Cada registro de la tabla de hechos representa el resultado oficial de un piloto, conduciendo un auto de una escudería, en un Gran Premio del Campeonato Mundial.** Equivale a una fila de results.csv (identificada por resultId).")
p("**Ejemplo de un registro:** Max Verstappen, Red Bull, Gran Premio de Baréin 2023 (5 de marzo de 2023): largó 1.º, terminó 1.º, 25 puntos, 57 vueltas, estado «Finished».")
lista([
    "**Es el grano atómico** disponible para el proceso de resultados. A partir de él se puede agregar por temporada, década, escudería, país o categoría sin perder información.",
    "**No se usa «piloto por carrera»** como grano porque, en las primeras temporadas, un piloto podía compartir autos y tener más de un resultado en el mismo Gran Premio. Por eso la unicidad se garantiza con id_resultado_origen.",
    "**Queda fuera del grano** el detalle por vuelta, las paradas en boxes y la clasificación (DataMarts 2 y 3). Las carreras sprint se identifican en la dimensión Carrera, pero sus resultados no forman parte de este hecho.",
    "**Tipo de tabla de hechos:** transaccional; cada fila corresponde a un evento. Los puntos acumulados del campeonato se agregan como una métrica semiaditiva del mismo evento.",
    "**Volumen:** ≈ 26 700 registros para 1950–2024 y un crecimiento aproximado de 480 registros por temporada (24 carreras × 20 pilotos).",
])
p("Como referencia, la granularidad de los hechos de los DataMarts no seleccionados sería: fact_vuelta, una vuelta de un piloto en una carrera; fact_parada_boxes, una parada en boxes de un piloto en una carrera; fact_clasificacion, el resultado de un piloto en la clasificación de un Gran Premio; y fact_posicion_campeonato, la situación de un piloto o escudería en el campeonato después de una ronda.")

# ===========================================================================
# 4. MODELADO LÓGICO
# ===========================================================================
h1("4. Modelado Lógico del DataMart")

h2("4.1 Tablas de hechos y dimensiones con sus respectivos atributos")
p("El modelo lógico adopta un esquema en estrella: una tabla de hechos central, fact_resultado_carrera, rodeada por seis tablas de dimensiones desnormalizadas. Se descartó el esquema copo de nieve (por ejemplo, separar país o nacionalidad en tablas propias) porque las dimensiones son pequeñas (menos de 1 200 filas, salvo Tiempo) y la estrella simplifica las consultas, la carga ETL y la definición de los cubos OLAP.")
p("**Resumen del modelo lógico:** 7 tablas; 6 dimensiones con 51 atributos; 1 tabla de hechos con 32 columnas: 1 clave primaria, 6 claves foráneas, 3 dimensiones degeneradas, 14 métricas, 7 indicadores 0/1 y 1 columna de auditoría.")
seccion_horizontal()
p("La Figura 2 muestra todas las tablas con sus atributos, tipos de datos y claves (PK = clave primaria sustituta, FK = clave foránea, NK = clave natural única, DD = dimensión degenerada; el signo «?» indica que el atributo admite nulos). Después de la figura se detalla cada tabla con la descripción y el origen de cada atributo en el dataset (o la regla de transformación del ETL).")
figura(diagramas.exportar_png(BASE / "build")["logico"], Cm(23),
       "**Figura 2.** Modelo lógico en estrella del DataMart Rendimiento en Carrera.")
h3("Tabla de hechos: fact_resultado_carrera")
p("Contiene las claves foráneas hacia las seis dimensiones, tres dimensiones degeneradas (atributos del evento que no justifican una tabla propia), las métricas numéricas y siete indicadores 0/1. Los indicadores se almacenan como números para que puedan sumarse directamente en las consultas y en los cubos OLAP: la suma de es_victoria es el número de victorias.")
diccionario("fact_resultado_carrera", ANCHO_HORIZONTAL)
h3("Dimensión Tiempo: dim_tiempo")
p("Calendario diario de 1950 a 2030, generado por SQL antes del ETL. Usa una clave sustituta inteligente (AAAAMMDD), habitual en dimensiones de fecha.")
diccionario("dim_tiempo", ANCHO_HORIZONTAL)
h3("Dimensión Carrera: dim_carrera")
p("Un registro por Gran Premio. Conserva el sistema de puntuación vigente para interpretar correctamente los puntos de cada época.")
diccionario("dim_carrera", ANCHO_HORIZONTAL)
h3("Dimensión Circuito: dim_circuito")
p("Circuitos donde se disputaron los Grandes Premios. El continente se deriva del país en el ETL para completar la jerarquía geográfica.")
diccionario("dim_circuito", ANCHO_HORIZONTAL)
h3("Dimensión Piloto: dim_piloto")
p("Pilotos que participaron en al menos un Gran Premio.")
diccionario("dim_piloto", ANCHO_HORIZONTAL)
h3("Dimensión Escudería: dim_escuderia")
p("Constructores o equipos con los que corrieron los pilotos.")
diccionario("dim_escuderia", ANCHO_HORIZONTAL)
h3("Dimensión Estado: dim_estado")
p("Estado con el que el piloto terminó la carrera. La categoría agrupa los 139 estados originales en siete grupos útiles para el análisis de confiabilidad.")
diccionario("dim_estado", ANCHO_HORIZONTAL)
seccion_vertical()

h2("4.2 Claves primarias, claves foráneas, claves sustitutas y relaciones entre las tablas")
tabla(["Tipo de clave", "Implementación en el modelo", "Ejemplo"], [
    ("Clave primaria", "Cada tabla tiene una clave primaria: la clave sustituta sk_* en cada dimensión y sk_resultado en la tabla de hechos.", "pk_dim_piloto (sk_piloto)"),
    ("Clave sustituta", "Entero generado por el DBMS (IDENTITY), sin significado de negocio; en Tiempo, clave inteligente AAAAMMDD.", "sk_piloto; sk_tiempo = 20230305"),
    ("Clave natural", "Identificador de la fuente, con restricción UNIQUE. El ETL la usa para buscar la clave sustituta.", "id_piloto_origen = drivers.driverId"),
    ("Clave foránea", "Seis columnas sk_* obligatorias en la tabla de hechos, una por dimensión.", "fk_fact_resultado_piloto"),
    ("Dimensión degenerada", "Atributos del evento sin tabla propia; id_resultado_origen es único y garantiza el grano.", "id_resultado_origen, numero_auto, codigo_posicion"),
], [22, 48, 30], titulo="Claves definidas en el modelo")
p("**¿Por qué claves sustitutas?** Independizan el Data Warehouse de los identificadores de la fuente, hacen más eficientes las uniones (enteros pequeños), permiten representar miembros especiales como «Desconocido» y dejan abierta la posibilidad de historizar cambios (tipo 2) sin modificar la tabla de hechos.")
p("**Dimensiones de cambio lento:** todas usan el tipo 1 (sobrescritura), porque sus atributos descriptivos no cambian con el tiempo o, cuando cambian (como el nombre comercial de una escudería: Toro Rosso → AlphaTauri), la fuente ya los registra como un miembro nuevo.")
p("**Miembro desconocido:** las dimensiones Circuito, Piloto, Escudería y Estado tienen una fila con clave -1 («Desconocido»). Si un resultado referencia un valor inexistente, el ETL asigna -1 en lugar de descartar el hecho, lo que preserva los totales. Un resultado sin carrera válida se rechaza, porque la carrera determina la fecha y el circuito.")
p("**Relaciones entre las tablas:** cada dimensión se relaciona con la tabla de hechos mediante una relación uno a muchos (1:N): un miembro de la dimensión puede aparecer en muchos resultados, y cada resultado referencia exactamente un miembro de cada dimensión.")
tabla(["Dimensión (lado 1)", "Columna en la tabla de hechos (lado N)", "Restricción", "Regla de negocio"], [
    ("dim_tiempo", "sk_tiempo", "fk_fact_resultado_tiempo", "Cada resultado ocurre en una fecha"),
    ("dim_carrera", "sk_carrera", "fk_fact_resultado_carrera", "Cada resultado pertenece a un Gran Premio"),
    ("dim_circuito", "sk_circuito", "fk_fact_resultado_circuito", "Cada resultado se obtiene en un circuito"),
    ("dim_piloto", "sk_piloto", "fk_fact_resultado_piloto", "Cada resultado corresponde a un piloto"),
    ("dim_escuderia", "sk_escuderia", "fk_fact_resultado_escuderia", "El piloto corre con una escudería en esa carrera"),
    ("dim_estado", "sk_estado", "fk_fact_resultado_estado", "Cada resultado tiene un estado final"),
], [20, 22, 28, 30], titulo="Relaciones del esquema en estrella")

h2("4.3 Métricas de la tabla de hechos clasificadas como aditivas, semiaditivas o no aditivas")
p("Las métricas de fact_resultado_carrera se clasifican según las dimensiones a lo largo de las cuales pueden sumarse con significado:")
tabla(["Métrica", "Clasificación", "Agregación válida", "Justificación"], [
    ("puntos, puntos_sistema_actual", "Aditiva", "SUM en todas las dimensiones", "Los puntos de varias carreras, pilotos o escuderías se suman (base de los campeonatos)."),
    ("vueltas_completadas", "Aditiva", "SUM", "Total de vueltas recorridas por piloto, escudería o temporada."),
    ("posiciones_ganadas", "Aditiva", "SUM, AVG", "Total o promedio de posiciones ganadas en una temporada o en una trayectoria."),
    ("es_victoria, es_podio, es_pole, es_en_puntos, es_vuelta_rapida, es_finalizado, es_abandono", "Aditiva (indicador 0/1)", "SUM = conteo", "La suma del indicador cuenta victorias, podios, poles, abandonos, etc."),
    ("puntos_acumulados_temporada", "Semiaditiva", "SUM entre pilotos de una misma ronda; en el tiempo, último valor o MAX", "Es un saldo acumulado: sumarlo entre rondas cuenta los mismos puntos varias veces."),
    ("posicion_salida, posicion_final, orden_llegada, posicion_campeonato, ranking_vuelta_rapida", "No aditiva", "MIN, AVG, moda, conteos", "Son valores ordinales: sumar posiciones no tiene significado."),
    ("tiempo_carrera_ms", "No aditiva", "AVG, MIN", "Depende de la longitud de cada carrera; sumar tiempos de distintos pilotos no tiene significado."),
    ("tiempo_vuelta_rapida_ms, velocidad_vuelta_rapida_kmh", "No aditiva", "MIN, MAX, AVG", "Miden ritmo, no cantidad."),
    ("edad_piloto", "No aditiva", "AVG, MIN, MAX", "Atributo medido en el momento del evento."),
    ("Indicadores derivados (tasas y porcentajes)", "No aditivos", "Se recalculan desde sus componentes", "Ejemplo: tasa de abandono = Σ es_abandono / N.º participaciones; nunca se promedian porcentajes."),
], [28, 16, 24, 32], titulo="Clasificación de las métricas")
p("**Regla para la métrica semiaditiva:** si por autos compartidos un piloto tiene más de un registro en la misma carrera, puntos_acumulados_temporada y posicion_campeonato se cargan solo en el registro con mejor orden de llegada (en los demás quedan nulos), para no duplicar el saldo al sumar entre pilotos. Para obtener el valor de una temporada se toma el de la última ronda, como en la siguiente consulta (campeón de cada temporada):")
extracto("04_consultas_objetivos.sql", "SELECT DISTINCT ON (c.temporada)", "ORDER BY c.temporada, c.ronda DESC;")

h2("4.4 Verificación de que el modelo lógico permite responder los objetivos del punto 2")
p("La siguiente matriz comprueba que cada objetivo específico puede responderse con las métricas y los atributos del modelo lógico:")
tabla(["OE", "Métricas de la tabla de hechos", "Dimensiones y atributos", "Consulta", "Cubierto"], [
    ("OE1", "es_pole, es_victoria, posiciones_ganadas", "Carrera (temporada), Circuito, Escudería", "Anexo B, OE1", "Sí"),
    ("OE2", "es_victoria, es_podio, puntos", "Carrera (temporada), Tiempo (década), Escudería", "Anexo B, OE2", "Sí"),
    ("OE3", "es_abandono, es_finalizado", "Estado (categoría), Escudería, Carrera, Circuito", "Anexo B, OE3", "Sí"),
    ("OE4", "puntos_sistema_actual, es_victoria, es_podio, edad_piloto, puntos_acumulados_temporada, posicion_campeonato", "Piloto, Carrera (temporada, ronda)", "Anexo B, OE4", "Sí"),
    ("OE5", "posiciones_ganadas, es_abandono, es_pole, es_victoria", "Circuito (continente, país, circuito)", "Anexo B, OE5", "Sí"),
    ("OE6", "tiempo_vuelta_rapida_ms, velocidad_vuelta_rapida_kmh", "Circuito, Carrera (temporada)", "Anexo B, OE6", "Sí"),
], [8, 36, 30, 14, 12], titulo="Trazabilidad entre objetivos y modelo lógico", centradas=(0, 3, 4))
p("Además de la matriz, para cada objetivo se escribió una consulta analítica (Anexo B), y todas se ejecutaron correctamente sobre el modelo implementado en PostgreSQL 16 con datos de prueba. Los resultados reales se obtendrán después de la carga ETL. Como ejemplo, la consulta del OE2 calcula la participación de cada escudería en las victorias, los podios y los puntos de cada temporada:")
extracto("04_consultas_objetivos.sql", "WITH por_escuderia AS", "ORDER BY temporada, puntos DESC;")

# ===========================================================================
# 5. MODELADO FÍSICO
# ===========================================================================
h1("5. Modelado Físico del DataMart")

h2("5.1 Implementación del modelo físico en un DBMS: tablas de dimensiones y hechos con sus tipos de datos, restricciones, claves e índices")
p("El modelo físico se implementó en PostgreSQL 16, creando las seis tablas de dimensiones y la tabla de hechos con sus tipos de datos, restricciones, claves e índices.")
h3("Plataforma y convenciones")
tabla(["Aspecto", "Decisión"], [
    ("DBMS", "PostgreSQL 16: software libre, con columnas IDENTITY, restricciones CHECK, índices parciales y funciones de ventana; se conecta por JDBC con Apache Hop y con las herramientas OLAP."),
    ("Base de datos", "dw_formula1, codificación UTF-8."),
    ("Esquema", "dw_f1, que separa los objetos del DataMart; las tablas de preparación del ETL podrán ubicarse en otro esquema."),
    ("Nombres de tablas", "Prefijo dim_ para dimensiones y fact_ para hechos; en español, minúsculas y sin tildes."),
    ("Nombres de columnas", "sk_ clave sustituta, id_*_origen clave natural, es_ indicador 0/1."),
    ("Restricciones e índices", "pk_, fk_, uq_, ck_ e ix_ seguidos del nombre de la tabla y el propósito."),
], [28, 72], titulo="Decisiones de implementación")
h3("Tipos de datos")
tabla(["Dato", "Tipo físico", "Justificación"], [
    ("Claves sustitutas de dimensiones", "INTEGER IDENTITY", "Generadas por el DBMS; rango suficiente para cualquier dimensión."),
    ("Clave sustituta de hechos", "BIGINT IDENTITY", "Sin límite práctico de crecimiento."),
    ("Clave de tiempo", "INTEGER (AAAAMMDD)", "Legible y ordenable; se calcula sin consultar la dimensión."),
    ("Posiciones, vueltas, rondas, indicadores", "SMALLINT", "Valores pequeños (2 bytes). Los indicadores 0/1 se pueden sumar, a diferencia de BOOLEAN."),
    ("Puntos", "NUMERIC(5,2) / NUMERIC(6,2)", "Admiten medios puntos sin errores de redondeo de punto flotante."),
    ("Tiempos", "BIGINT / INTEGER (milisegundos)", "Permiten promedios, mínimos y diferencias, lo que no es posible con el texto «1:27.452»."),
    ("Velocidad", "NUMERIC(7,3)", "Conserva la precisión de la fuente (milésimas de km/h)."),
    ("Coordenadas", "NUMERIC(9,6)", "Seis decimales (≈ 0,1 m) dentro de los rangos válidos de latitud y longitud."),
    ("Fechas y horas", "DATE, TIME, TIMESTAMP", "Tipos nativos que permiten aritmética de fechas (por ejemplo, la edad del piloto)."),
    ("Textos", "VARCHAR(n), CHAR(3)", "Longitud acotada al dominio; CHAR(3) para el código fijo del piloto."),
], [30, 26, 44], titulo="Criterios para la elección de tipos de datos")
h3("Restricciones y claves")
lista([
    "**Claves primarias** en las siete tablas y **claves naturales únicas** (UNIQUE) en las dimensiones; en Carrera también es única la combinación temporada y ronda.",
    "**Seis claves foráneas** obligatorias (NOT NULL) desde la tabla de hechos hacia cada dimensión.",
    "**Reglas de dominio (CHECK):** posiciones mayores que cero, puntos no negativos, edad entre 14 y 70 años, coordenadas válidas, continentes y categorías de estado de una lista cerrada, y código de posición con el patrón ^([0-9]{1,2}|R|D|E|W|F|N)$.",
    "**Coherencia de los indicadores:** por ejemplo, es_victoria = 1 si y solo si posicion_final = 1, y es_abandono = 1 si y solo si codigo_posicion = 'R'. Así, los conteos de los cubos OLAP siempre coinciden con las posiciones.",
    "**Dimensión Tiempo:** la clave debe coincidir con la fecha (sk_tiempo = AAAAMMDD) y la década con el año.",
])
h3("Índices")
p("Además de los índices que PostgreSQL crea automáticamente para las claves primarias y las restricciones UNIQUE (usados por el ETL para buscar las claves sustitutas), se definieron quince índices orientados a las consultas analíticas:")
tabla(["Índice", "Tabla (columnas)", "Propósito"], [
    ("ix_fact_resultado_tiempo, _carrera, _circuito, _estado", "fact (sk_tiempo), (sk_carrera), (sk_circuito), (sk_estado)", "Uniones y filtros por dimensión"),
    ("ix_fact_resultado_piloto_tiempo", "fact (sk_piloto, sk_tiempo)", "Series históricas por piloto; también cubre los filtros por piloto"),
    ("ix_fact_resultado_escuderia_tiempo", "fact (sk_escuderia, sk_tiempo)", "Series históricas por escudería"),
    ("ix_fact_resultado_victorias", "fact (sk_escuderia, sk_piloto) WHERE es_victoria = 1", "Índice parcial para rankings de victorias (≈ 4 % de las filas)"),
    ("ix_dim_tiempo_anio_mes, ix_dim_tiempo_decada", "dim_tiempo (anio, mes), (decada)", "Navegación de la jerarquía temporal"),
    ("ix_dim_carrera_temporada", "dim_carrera (temporada)", "Filtros por temporada"),
    ("ix_dim_circuito_pais", "dim_circuito (continente, pais)", "Jerarquía geográfica"),
    ("ix_dim_piloto_nacionalidad, ix_dim_piloto_apellido", "dim_piloto (nacionalidad), (apellido)", "Filtros y búsqueda de pilotos"),
    ("ix_dim_escuderia_nombre", "dim_escuderia (nombre_escuderia)", "Filtros por escudería"),
    ("ix_dim_estado_categoria", "dim_estado (categoria_estado)", "Agrupación de causas de abandono"),
], [36, 34, 30], titulo="Índices del DataMart")
h3("Script de creación de las tablas de dimensiones y de hechos (01_crear_esquema_y_tablas.sql)")
codigo("01_crear_esquema_y_tablas.sql")
h3("Script de creación de índices (02_crear_indices.sql)")
codigo("02_crear_indices.sql")

h2("5.2 Relaciones entre las tablas e integridad referencial")
p("Las relaciones entre la tabla de hechos y las dimensiones se crearon como claves foráneas en el DBMS. Todas son obligatorias (NOT NULL) y usan la acción por defecto NO ACTION: no se puede insertar un hecho que apunte a un miembro inexistente ni eliminar un miembro de una dimensión mientras existan hechos que lo referencien. Así, la integridad referencial se garantiza en la base de datos y no depende del proceso ETL.")
p("Los scripts se ejecutaron en PostgreSQL 16.15. Las siguientes tablas, obtenidas de los catálogos del sistema, confirman las tablas creadas con sus claves, restricciones e índices, las seis claves foráneas y las filas generadas por el script de datos iniciales:")
bloques = leer_evidencia()
tabla(["Tabla", "Columnas", "PK", "FK", "UNIQUE", "CHECK", "Índices"], bloques[0][1:],
      [34, 12, 9, 9, 12, 12, 12], titulo="Tablas creadas en el esquema dw_f1 (catálogo de PostgreSQL)", centradas=(1, 2, 3, 4, 5, 6))
tabla(["Restricción", "Tabla", "Referencia"], bloques[1][1:], [36, 36, 28],
      titulo="Claves foráneas creadas (hechos → dimensiones)")
tabla(["Tabla", "Filas", "Desde", "Hasta"], bloques[2][1:], [34, 22, 22, 22],
      titulo="Filas cargadas por el script de datos iniciales", centradas=(1, 2, 3))
p("Para comprobar la integridad referencial y las reglas de dominio se ejecutó el script de pruebas (Anexo C). Cada operación inválida es rechazada por el DBMS con la restricción correspondiente, y al final solo permanece el registro válido de ejemplo, que se descarta con ROLLBACK:")
descripciones = {
    "Prueba 1": ("Insertar un hecho con un piloto inexistente", "fk_fact_resultado_piloto"),
    "Prueba 2": ("Marcar como victoria un segundo puesto", "ck_fact_victoria"),
    "Prueba 3": ("Cargar dos veces el mismo resultado", "uq_fact_resultado_origen"),
    "Prueba 4": ("Eliminar un piloto que tiene resultados", "fk_fact_resultado_piloto"),
    "Prueba 5": ("Registrar puntos negativos", "ck_fact_puntos"),
}
filas_pruebas = []
for num, _desc, error in leer_pruebas():
    operacion, restriccion = descripciones[num]
    filas_pruebas.append((num.replace("Prueba ", ""), operacion, restriccion, "Rechazada: " + error))
tabla(["N.º", "Operación inválida", "Restricción", "Respuesta de PostgreSQL"], filas_pruebas,
      [6, 24, 24, 46], titulo="Resultado de las pruebas de integridad", centradas=(0,))

h2("5.3 Estructura física orientada a facilitar las consultas analíticas y la posterior carga mediante los procesos ETL")
h3("Orientación a las consultas analíticas")
lista([
    "**Esquema en estrella:** cualquier consulta necesita como máximo una unión por dimensión, sin cadenas de uniones.",
    "**Métricas precalculadas:** posiciones ganadas, puntos normalizados, edad del piloto e indicadores 0/1 se calculan una sola vez en el ETL, no en cada consulta.",
    "**Indicadores sumables:** victorias, podios o abandonos se obtienen con SUM, lo que facilita definir las medidas de los cubos OLAP.",
    "**Jerarquías precalculadas:** década, trimestre, continente y categoría de estado están almacenados como atributos, listos para el drill-down.",
    "**Índices** sobre las claves foráneas, combinaciones frecuentes (piloto–tiempo, escudería–tiempo) y un índice parcial de victorias (punto 5.1).",
    "**Consultas de verificación:** las seis consultas del Anexo B se ejecutan directamente sobre este modelo.",
])
h3("Orientación a la carga mediante procesos ETL")
lista([
    "**Orden de carga:** (1) dim_tiempo, ya generada por SQL (Anexo A); (2) dimensiones Estado, Circuito, Piloto, Escudería y Carrera; (3) tabla de hechos.",
    "**Búsqueda de claves:** cada fila de results.csv obtiene sus claves sustitutas buscando la clave natural (id_*_origen) en cada dimensión; si no existe, se asigna el miembro desconocido (-1).",
    "**Recarga sin duplicados:** UNIQUE (id_resultado_origen) impide duplicar resultados si el proceso se ejecuta más de una vez; el ETL usará inserción o actualización según la clave natural.",
    "**Auditoría:** la columna fecha_carga registra cuándo se cargó cada hecho.",
    "**Transformaciones previstas:** \\N → NULL; tiempos «m:ss.mmm» → milisegundos; cálculo de posiciones ganadas, indicadores, puntos normalizados y edad; continente según el país; categoría del estado; sistema de puntos según la temporada; puntos acumulados desde driver_standings por (raceId, driverId).",
], numerada=True)
tabla(["Temporadas", "Puntos por posición (1.º al 10.º)", "Vuelta más rápida"], [
    ("1950–1959", "8-6-4-3-2", "+1 punto"),
    ("1960", "8-6-4-3-2-1", "—"),
    ("1961–1990", "9-6-4-3-2-1", "—"),
    ("1991–2002", "10-6-4-3-2-1", "—"),
    ("2003–2009", "10-8-6-5-4-3-2-1", "—"),
    ("2010–2018", "25-18-15-12-10-8-6-4-2-1", "—"),
    ("2019–2024", "25-18-15-12-10-8-6-4-2-1", "+1 punto si termina entre los 10 primeros"),
    ("2025 en adelante", "25-18-15-12-10-8-6-4-2-1", "—"),
], [24, 40, 36], titulo="Regla para dim_carrera.sistema_puntos", centradas=(0,))
p("El sistema 2010–actual es la base de puntos_sistema_actual. Hasta 1990 solo contaban los mejores resultados de cada piloto (descartes); por eso los puntos acumulados del campeonato se toman de la fuente y no se recalculan.")
tabla(["Categoría", "Estados de origen (ejemplos)"], [
    ("Finalizó", "Finished"),
    ("Finalizó con vueltas de retraso", "+1 Lap, +2 Laps, etc."),
    ("Falla mecánica", "Engine, Gearbox, Transmission, Hydraulics, Brakes, Suspension, Electrical, Power Unit, etc."),
    ("Accidente o colisión", "Accident, Collision, Collision damage, Spun off, etc."),
    ("Descalificación", "Disqualified, Excluded"),
    ("No largó o no clasificó", "Did not qualify, Did not prequalify, Withdrew, Not classified, 107% Rule"),
    ("Otro", "Estados restantes (por ejemplo, Retired sin causa especificada o enfermedad del piloto)"),
], [32, 68], titulo="Regla para dim_estado.categoria_estado")
p("Para ejecutar la implementación completa se usan los siguientes comandos (los scripts 03 a 05 están en los anexos):")
for linea in ("createdb -U postgres -E UTF8 -T template0 dw_formula1",
              "psql -U postgres -d dw_formula1 -f 01_crear_esquema_y_tablas.sql",
              "psql -U postgres -d dw_formula1 -f 02_crear_indices.sql",
              "psql -U postgres -d dw_formula1 -f 03_datos_iniciales.sql",
              "psql -U postgres -d dw_formula1 -f 05_pruebas_integridad.sql"):
    parrafo = doc.add_paragraph(linea)
    parrafo.paragraph_format.space_after = Pt(0)
    parrafo.paragraph_format.left_indent = Cm(1)
doc.add_paragraph()

# ===========================================================================
# CONCLUSIONES, REFERENCIAS Y ANEXOS
# ===========================================================================
h1("Conclusiones")
lista([
    "**Punto 1:** se seleccionó un tema con un problema analítico propio (el rendimiento competitivo en la Fórmula 1) y un conjunto de datos público de Kaggle con setenta y cinco temporadas, varios procesos de negocio y problemas reales de calidad de datos.",
    "**Punto 2:** se definieron un objetivo general y seis objetivos específicos medibles, cada uno con indicadores, consultas, reportes y cuadros de mando previstos, y con los elementos del diseño que se derivan de él.",
    "**Punto 3:** de tres DataMarts propuestos se seleccionó el de Rendimiento en Carrera mediante una evaluación ponderada; su modelo conceptual tiene un hecho y seis dimensiones, y su grano es el resultado de un piloto con un auto en un Gran Premio.",
    "**Punto 4:** el modelo lógico en estrella define todos los atributos, las claves primarias, foráneas y sustitutas, las relaciones 1:N y la clasificación de las métricas; la matriz de trazabilidad confirma que cubre los seis objetivos.",
    "**Punto 5:** el modelo físico está implementado y probado en PostgreSQL 16, con integridad referencial, reglas de dominio, índices analíticos y la dimensión Tiempo ya generada para la carga ETL.",
])
p("**Próximos pasos (segunda presentación):** desarrollar los procesos ETL con Apache Hop para extraer los CSV, depurarlos y cargar el DataMart; crear el cubo OLAP con las jerarquías definidas; construir los reportes R1 a R5; y diseñar los cuadros de mando interactivos CM1 y CM2.")

h1("Referencias")
for ref in (
    "Ergast Developer API. (s. f.). Ergast Motor Racing Developer API: documentación y base de datos histórica de la Fórmula 1. http://ergast.com/mrd/",
    "Kimball, R. y Ross, M. (2013). The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling (3.ª ed.). Wiley.",
    "Rao, R. (2024). Formula 1 World Championship (1950 – 2024) [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020",
    "The PostgreSQL Global Development Group. (2024). PostgreSQL 16 Documentation. https://www.postgresql.org/docs/16/",
):
    parrafo = doc.add_paragraph(ref)
    parrafo.paragraph_format.left_indent = Cm(1)
    parrafo.paragraph_format.first_line_indent = Cm(-1)

h1("Anexos")
p("Los scripts 01_crear_esquema_y_tablas.sql y 02_crear_indices.sql se incluyen completos en el punto 5.1.")
h2("Anexo A. 03_datos_iniciales.sql")
codigo("03_datos_iniciales.sql")
h2("Anexo B. 04_consultas_objetivos.sql")
codigo("04_consultas_objetivos.sql")
h2("Anexo C. 05_pruebas_integridad.sql")
codigo("05_pruebas_integridad.sql")

# ---------------------------------------------------------------------------
# Guardar y exportar a PDF
# ---------------------------------------------------------------------------
doc.save(SALIDA_DOCX)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SALIDA_DOCX.parent), str(SALIDA_DOCX)],
               check=True, capture_output=True)
print("Generados:", SALIDA_DOCX.name, "y", SALIDA_DOCX.with_suffix(".pdf").name)

"""Construye la primera presentación en Word y PDF (texto en Arial 12).

Uso (desde esta carpeta):
    NODE_PATH=$(npm root -g) python3 construir_docx.py

Requiere python-docx, LibreOffice (soffice) para exportar a PDF y Node.js con
Playwright para dibujar el diagrama del modelo físico. Escribe
../Primera_Presentacion_DW_Vuelos.docx y ../Primera_Presentacion_DW_Vuelos.pdf.
"""
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import diagrama_fisico

BASE = Path(__file__).resolve().parent
SQL = BASE.parent.parent / "sql"
SALIDA_DOCX = BASE.parent / "Primera_Presentacion_DW_Vuelos.docx"

doc = Document()

# Todo en Arial 12, negro, interlineado sencillo
for nombre in ("Normal", "List Bullet"):
    estilo = doc.styles[nombre]
    estilo.font.name = "Arial"
    estilo.font.size = Pt(12)
    estilo.font.color.rgb = RGBColor(0, 0, 0)
    rfonts = estilo.element.get_or_add_rPr().get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(atributo), "Arial")
    estilo.paragraph_format.space_before = Pt(0)
    estilo.paragraph_format.space_after = Pt(3)
    estilo.paragraph_format.line_spacing = 1.0

seccion = doc.sections[0]
seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
seccion.left_margin = seccion.right_margin = Cm(2.5)
seccion.top_margin = seccion.bottom_margin = Cm(2.5)


def _runs(parrafo, texto):
    """Agrega texto al párrafo; lo encerrado entre ** va en negrita."""
    for i, trozo in enumerate(texto.split("**")):
        if trozo:
            parrafo.add_run(trozo).bold = bool(i % 2)


def p(texto, centrado=False):
    parrafo = doc.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER if centrado else WD_ALIGN_PARAGRAPH.JUSTIFY
    _runs(parrafo, texto)
    return parrafo


def titulo(texto):
    parrafo = doc.add_paragraph()
    parrafo.paragraph_format.space_before = Pt(6)
    parrafo.paragraph_format.keep_with_next = True
    parrafo.add_run(texto).bold = True


def vinetas(elementos):
    for e in elementos:
        parrafo = doc.add_paragraph(style="List Bullet")
        parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        parrafo.paragraph_format.space_after = Pt(1)
        _runs(parrafo, e)


def tabla(encabezados, filas, anchos_cm):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.autofit = False
    for fila_datos in [encabezados] + filas:
        celdas = t.rows[0].cells if fila_datos is encabezados else t.add_row().cells
        for j, valor in enumerate(fila_datos):
            par = celdas[j].paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            if fila_datos is encabezados:
                par.add_run(valor).bold = True
            else:
                _runs(par, valor)
    for j, columna in enumerate(t.columns):
        columna.width = Cm(anchos_cm[j])
        for celda in columna.cells:
            celda.width = Cm(anchos_cm[j])
    for fila in t.rows:
        cs = OxmlElement("w:cantSplit")
        cs.set(qn("w:val"), "true")
        fila._tr.get_or_add_trPr().append(cs)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def nueva_seccion(horizontal):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.LANDSCAPE if horizontal else WD_ORIENT.PORTRAIT
    s.page_width, s.page_height = (Cm(29.7), Cm(21)) if horizontal else (Cm(21), Cm(29.7))
    s.top_margin = s.bottom_margin = Cm(2 if horizontal else 2.5)
    s.left_margin = s.right_margin = Cm(1.5 if horizontal else 2.5)


def script_sin_comentarios(archivo):
    """Líneas del script sin comentarios ni COMMENT ON, con espacios simplificados."""
    lineas = []
    for linea in (SQL / archivo).read_text(encoding="utf-8").splitlines():
        if linea.lstrip().startswith(("--", "COMMENT ON")):
            continue
        if not linea.strip():
            if lineas and lineas[-1].strip():
                lineas.append("")
            continue
        sangria = len(linea) - len(linea.lstrip(" "))
        lineas.append(" " * sangria + re.sub(r"\s{2,}", " ", linea.strip()))
    return lineas


def codigo(lineas):
    for linea in lineas:
        parrafo = doc.add_paragraph()
        parrafo.paragraph_format.space_after = Pt(0)
        sangria = min(len(linea) - len(linea.lstrip(" ")), 8)  # las continuaciones no se alinean en Arial
        parrafo.paragraph_format.left_indent = Cm(0.25 * sangria)
        parrafo.add_run(linea.strip())


# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
p("**[Universidad] – Base de Datos III – Proyecto: Implementación de un Data Warehouse**", centrado=True)
p("**Primera Presentación (puntos 1 a 5): Data Warehouse de puntualidad de vuelos en EE. UU. (2015)**", centrado=True)
p("Integrantes: Jhonatan Moisés Villca, [Integrante 2], [Integrante 3] – Docente: Rodnie Montaño Aguilera", centrado=True)

# ---------------------------------------------------------------------------
# 1. Tema
# ---------------------------------------------------------------------------
titulo("1. Tema del Proyecto")
p("**Tema:** análisis de la puntualidad, los retrasos y las cancelaciones de los vuelos comerciales nacionales de Estados Unidos en 2015. **Conjunto de datos:** «2015 Flight Delays and Cancellations» de Kaggle, publicado por el Departamento de Transporte de EE. UU. con datos de la Oficina de Estadísticas de Transporte (BTS). Tiene tres archivos CSV: flights.csv (≈ 5,8 millones de vuelos con fecha, aerolínea, número de vuelo, aeropuertos de origen y destino, horarios programados y reales, retrasos, tiempos de rodaje y de vuelo, distancia, cancelación, desvío y minutos de retraso por causa), airlines.csv (14 aerolíneas) y airports.csv (322 aeropuertos con ciudad, estado y coordenadas).")
p("**Suficiencia de los datos:** cada vuelo es un evento medible con métricas numéricas (minutos de retraso, tiempos, distancia) y con descriptores que forman dimensiones con jerarquías: fecha → mes → trimestre, hora → franja horaria y aeropuerto → ciudad → estado → región. El volumen y los problemas de calidad (horas en formato hhmm, valores vacíos en vuelos cancelados o desviados, aeropuertos con códigos numéricos en lugar del código IATA en octubre) justifican un Data Warehouse y un proceso ETL.")
p("**Contexto y necesidad de análisis:** según la BTS, un vuelo está retrasado si llega 15 minutos o más después de lo programado, y las aerolíneas informan la causa (la propia aerolínea, el clima, el sistema aéreo nacional, la seguridad o la llegada tardía del avión). Los datos están en un solo archivo plano, útil para registrar vuelos pero no para analizarlos. La necesidad es **saber dónde, cuándo y por qué se producen los retrasos y las cancelaciones** (por aerolínea, aeropuerto, ruta, horario y causa), para que aerolíneas, aeropuertos y pasajeros tomen mejores decisiones. No es un tema de ventas ni de inventario: es el análisis del desempeño operativo de un sistema de transporte.")

# ---------------------------------------------------------------------------
# 2. Objetivos
# ---------------------------------------------------------------------------
titulo("2. Objetivos del Data Warehouse")
p("**Objetivo general:** implementar un Data Warehouse con un DataMart de Puntualidad de Vuelos que integre los vuelos de 2015 para analizar la puntualidad, los retrasos y las cancelaciones por aerolínea, aeropuerto, ruta y período, mediante indicadores, consultas, cubos OLAP, reportes y cuadros de mando.")
p("**Objetivos específicos** (medibles con el indicador indicado):")
tabla(["Cód.", "Objetivo específico", "Indicador"], [
    ["OE1", "Medir la puntualidad de cada aerolínea por mes.", "% de vuelos puntuales"],
    ["OE2", "Cuantificar las cancelaciones y los desvíos por aerolínea y motivo.", "% de cancelación y de desvío"],
    ["OE3", "Identificar qué causas generan más minutos de retraso.", "% de minutos por causa"],
    ["OE4", "Determinar los aeropuertos y rutas con mayor retraso.", "Retraso promedio de llegada"],
    ["OE5", "Analizar los retrasos según la franja horaria y el día de la semana.", "Retraso promedio de salida"],
    ["OE6", "Evaluar la eficiencia en tierra de cada aeropuerto.", "Tiempo promedio de rodaje"],
], [1.4, 9.4, 5.2])
p("Estos objetivos definen el hecho (vuelo), las dimensiones (fecha, hora, aerolínea, aeropuerto y motivo de cancelación), las métricas, la granularidad y los reportes y cuadros de mando de la segunda presentación.")

# ---------------------------------------------------------------------------
# 3. Modelado conceptual
# ---------------------------------------------------------------------------
titulo("3. Modelado Conceptual del DataMart")
p("**Tres DataMarts posibles:**")
vinetas([
    "**DM1 Puntualidad de Vuelos:** cada vuelo con sus retrasos, cancelación y desvío.",
    "**DM2 Causas de Retraso:** minutos de retraso de cada vuelo repartidos por causa.",
    "**DM3 Operaciones Aeroportuarias:** resumen diario de salidas, llegadas y cancelaciones de cada aeropuerto.",
])
p("**DataMart seleccionado: DM1**, porque tiene el detalle de cada vuelo (los otros dos se pueden obtener de él), responde los seis objetivos y sus dimensiones se reutilizan en DM2 y DM3.")
p("**Modelo conceptual:** proceso de negocio «operación de un vuelo programado»; hecho **Vuelo**; dimensiones con sus jerarquías: Fecha (año → trimestre → mes → fecha, y día de la semana), Hora de salida (franja horaria → hora), Aerolínea, Aeropuerto (región → estado → ciudad → aeropuerto), que se usa dos veces, como origen y como destino, y Motivo de cancelación.")
p("**Granularidad:** cada registro de la tabla de hechos es **un vuelo programado de una aerolínea en una fecha** (una fila de flights.csv), identificado por la fecha, la aerolínea, el número de vuelo, el aeropuerto de origen y la hora programada de salida; ≈ 5,8 millones de registros.")

# ---------------------------------------------------------------------------
# 4. Modelado lógico
# ---------------------------------------------------------------------------
titulo("4. Modelado Lógico del DataMart")
p("Esquema en estrella. Cada dimensión se relaciona 1:N con la tabla de hechos mediante su clave sustituta (PK) y la clave foránea (FK) correspondiente:")
tabla(["Tabla", "Atributos"], [
    ["fact_vuelo", "PK sk_vuelo; FK sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino, sk_motivo_cancelacion; numero_vuelo, matricula_avion, salida_programada; métricas en minutos: retraso_salida_min, retraso_llegada_min, taxi_salida_min, taxi_llegada_min, tiempo_aire_min, retraso por causa (aerolínea, clima, sistema aéreo, seguridad, avión tardío); distancia_millas; indicadores 0/1: es_cancelado, es_desviado, es_retrasado, es_puntual"],
    ["dim_fecha", "PK sk_fecha (AAAAMMDD); fecha, dia_semana, es_fin_de_semana, mes, trimestre, anio"],
    ["dim_hora", "PK sk_hora (0 a 23); hora_texto, franja_horaria"],
    ["dim_aerolinea", "PK sk_aerolinea; codigo_iata, nombre_aerolinea"],
    ["dim_aeropuerto", "PK sk_aeropuerto; codigo_iata, nombre_aeropuerto, ciudad, estado, region, latitud, longitud"],
    ["dim_motivo_cancelacion", "PK sk_motivo_cancelacion; codigo_motivo (N, A, B, C, D), descripcion"],
], [5.3, 10.7])
vinetas([
    "**Claves:** las claves sustitutas (sk_*) son enteros generados por el DBMS; los códigos IATA del dataset son claves naturales únicas que el ETL usa para buscar la clave sustituta. dim_aeropuerto se relaciona dos veces con los hechos (origen y destino).",
    "**Métricas aditivas:** minutos de retraso (total y por causa), tiempos, distancia e indicadores 0/1 (su suma cuenta vuelos cancelados, retrasados o puntuales).",
    "**Métricas semiaditivas:** no hay en este hecho, porque cada vuelo es un evento independiente y no un saldo acumulado.",
    "**Métricas no aditivas:** porcentajes de puntualidad y de cancelación, y promedios; se recalculan desde sus componentes.",
])
p("**Verificación:** OE1 usa es_puntual por aerolínea y mes; OE2, es_cancelado y es_desviado por aerolínea y motivo; OE3, los minutos por causa; OE4, retraso_llegada_min por aeropuertos de origen y destino; OE5, retraso_salida_min por franja horaria y día; OE6, taxi_salida_min por aeropuerto de origen. Todos los objetivos se pueden responder con el modelo.")

# ---------------------------------------------------------------------------
# 5. Modelado físico
# ---------------------------------------------------------------------------
titulo("5. Modelado Físico del DataMart")
p("Se implementó en **PostgreSQL 16** (base y esquema dw_vuelos) con scripts SQL que crean las cinco dimensiones y la tabla de hechos, los índices y los datos fijos (fechas 2014–2016, las 24 horas y los motivos de cancelación).")
vinetas([
    "**Tipos de datos:** claves INTEGER/BIGINT IDENTITY; minutos y distancia SMALLINT (los retrasos negativos indican adelanto); indicadores SMALLINT; fecha DATE y hora programada TIME; códigos VARCHAR(3).",
    "**Restricciones e integridad referencial:** PK en todas las tablas, UNIQUE en los códigos IATA y en la clave natural del vuelo, seis FK obligatorias (dos hacia dim_aeropuerto) y reglas CHECK (distancia > 0, un vuelo cancelado debe tener motivo, es_retrasado = 1 solo si llegó con 15 minutos o más de retraso). Se probó que el DBMS rechaza aerolíneas inexistentes, vuelos duplicados y el borrado de aeropuertos con vuelos.",
    "**Índices y orientación al análisis y al ETL:** índices en cada FK, en (aerolínea, fecha), en la ruta (origen, destino) y un índice parcial de vuelos cancelados; la clave natural única permite recargar sin duplicar y el miembro «Desconocido» (-1) evita perder vuelos con códigos no encontrados.",
])
p("La Figura 1 muestra el modelo físico implementado, obtenido del catálogo de PostgreSQL: cada tabla con sus columnas, tipos de datos, claves y columnas obligatorias. El script de creación completo está en el Anexo.")

# Figura del modelo físico (página horizontal)
nueva_seccion(horizontal=True)
figura = doc.add_paragraph()
figura.alignment = WD_ALIGN_PARAGRAPH.CENTER
figura.add_run().add_picture(str(diagrama_fisico.exportar_png(BASE / "build")), width=Cm(26.5))
p("**Figura 1.** Modelo físico del DataMart Puntualidad de Vuelos en PostgreSQL 16 (esquema dw_vuelos).", centrado=True)
p("PK = clave primaria; FK = clave foránea; UK = forma parte de una restricción UNIQUE; NN = NOT NULL; IDENTITY = valor generado por el DBMS; ‖──< = relación 1:N. dim_aeropuerto se relaciona dos veces con fact_vuelo (origen y destino).", centrado=True)

# Anexo con el script del modelo físico
nueva_seccion(horizontal=False)
titulo("Anexo. Script del modelo físico (PostgreSQL 16)")
p("Scripts 01_crear_esquema_y_tablas.sql y 02_crear_indices.sql, sin los comentarios:")
codigo(script_sin_comentarios("01_crear_esquema_y_tablas.sql") + [""] + script_sin_comentarios("02_crear_indices.sql"))

doc.save(SALIDA_DOCX)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SALIDA_DOCX.parent), str(SALIDA_DOCX)],
               check=True, capture_output=True)
print("Generados:", SALIDA_DOCX.name, "y", SALIDA_DOCX.with_suffix(".pdf").name)

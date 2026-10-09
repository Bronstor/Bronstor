"""Construye la primera presentación en Word y PDF (texto en Arial 12).

Uso (desde esta carpeta):
    NODE_PATH=$(npm root -g) python3 construir_docx.py

Requiere python-docx, LibreOffice (soffice) para exportar a PDF y Node.js con
Playwright para dibujar los diagramas. Escribe
../Primera_Presentacion_DW_Vuelos.docx y ../Primera_Presentacion_DW_Vuelos.pdf.
"""
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import diagramas

BASE = Path(__file__).resolve().parent
SALIDA_DOCX = BASE.parent / "Primera_Presentacion_DW_Vuelos.docx"

doc = Document()

# Cuerpo en Arial 12, negro, interlineado 1,15
estilo = doc.styles["Normal"]
estilo.font.name = "Arial"
estilo.font.size = Pt(12)
estilo.font.color.rgb = RGBColor(0, 0, 0)
rfonts = estilo.element.get_or_add_rPr().get_or_add_rFonts()
for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
    rfonts.set(qn(atributo), "Arial")
estilo.paragraph_format.space_before = Pt(0)
estilo.paragraph_format.space_after = Pt(6)
estilo.paragraph_format.line_spacing = 1.15

seccion = doc.sections[0]
seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
seccion.left_margin = seccion.right_margin = Cm(2.5)
seccion.top_margin = seccion.bottom_margin = Cm(2.5)

numero_tabla = 0
numero_figura = 0


# ---------------------------------------------------------------------------
# Ayudantes
# ---------------------------------------------------------------------------
def parrafo(texto, centrado=False):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER if centrado else WD_ALIGN_PARAGRAPH.JUSTIFY
    par.add_run(texto)
    return par


def titulo1(texto):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(12)
    par.paragraph_format.space_after = Pt(6)
    par.paragraph_format.keep_with_next = True
    par.add_run(texto.upper()).bold = True


def titulo2(texto):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.keep_with_next = True
    par.add_run(texto).bold = True


def _sombrear(celda, color="D9D9D9"):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(shd)


def tabla(titulo_tabla, encabezados, filas, anchos_cm):
    """Tabla numerada: título arriba, encabezado sombreado y repetido en cada página."""
    global numero_tabla
    numero_tabla += 1
    cab = doc.add_paragraph()
    cab.paragraph_format.keep_with_next = True
    cab.paragraph_format.space_after = Pt(3)
    cab.add_run(f"Tabla {numero_tabla}. ").bold = True
    cab.add_run(titulo_tabla)

    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.autofit = False
    for fila_datos in [encabezados] + filas:
        es_cab = fila_datos is encabezados
        celdas = t.rows[0].cells if es_cab else t.add_row().cells
        for j, valor in enumerate(fila_datos):
            par = celdas[j].paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            par.add_run(valor).bold = es_cab
            if es_cab:
                _sombrear(celdas[j])
    for j, columna in enumerate(t.columns):
        columna.width = Cm(anchos_cm[j])
        for celda in columna.cells:
            celda.width = Cm(anchos_cm[j])
    for i, fila in enumerate(t.rows):
        trpr = fila._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        cs.set(qn("w:val"), "true")
        trpr.append(cs)
        if i == 0:
            th = OxmlElement("w:tblHeader")
            th.set(qn("w:val"), "true")
            trpr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def figura(ruta_png, ancho, titulo_figura, nota=None):
    """Figura numerada con su título debajo."""
    global numero_figura
    numero_figura += 1
    imagen = doc.add_paragraph()
    imagen.alignment = WD_ALIGN_PARAGRAPH.CENTER
    imagen.paragraph_format.keep_with_next = True
    imagen.add_run().add_picture(str(ruta_png), width=ancho)
    pie = doc.add_paragraph()
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pie.add_run(f"Figura {numero_figura}. ").bold = True
    pie.add_run(titulo_figura)
    if nota:
        parrafo(nota, centrado=True)


def nueva_seccion(horizontal):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.LANDSCAPE if horizontal else WD_ORIENT.PORTRAIT
    s.page_width, s.page_height = (Cm(29.7), Cm(21)) if horizontal else (Cm(21), Cm(29.7))
    s.top_margin = s.bottom_margin = Cm(2 if horizontal else 2.5)
    s.left_margin = s.right_margin = Cm(1.5 if horizontal else 2.5)


# ---------------------------------------------------------------------------
# Carátula (Times New Roman, como el modelo de la universidad)
# ---------------------------------------------------------------------------
def _times(run, negrita=False):
    run.bold = negrita
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    rf = run._element.get_or_add_rPr().get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(atributo), "Times New Roman")


def caratula():
    logo = doc.add_paragraph()
    logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo.paragraph_format.space_before = Pt(18)
    logo.paragraph_format.space_after = Pt(60)
    logo.add_run().add_picture(str(BASE / "logo_nur.png"), width=Cm(14.5))

    datos = [
        ("Materia / Asignatura:", ["Base de Datos III"]),
        ("Docente / Profesor:", ["Rodnie Montaño Aguilera"]),
        ("Estudiante / Integrantes:", ["• Jhonatan Moisés Villca", "• Pedro Visir Valda"]),
        ("Proyecto:", ["Análisis de la puntualidad, los retrasos y las cancelaciones de los vuelos comerciales nacionales de Estados Unidos en 2015"]),
    ]
    t = doc.add_table(rows=len(datos), cols=2)
    t.autofit = False
    for fila, (etiqueta, valores) in zip(t.rows, datos):
        celda_e, celda_v = fila.cells
        celda_e.width, celda_v.width = Cm(5.6), Cm(10.4)
        par = celda_e.paragraphs[0]
        par.paragraph_format.space_after = Pt(18)
        _times(par.add_run(etiqueta), negrita=True)
        for i, valor in enumerate(valores):
            par = celda_v.paragraphs[0] if i == 0 else celda_v.add_paragraph()
            par.paragraph_format.line_spacing = 2.0
            par.paragraph_format.space_after = Pt(18 if i == len(valores) - 1 else 0)
            if valor.startswith("• "):
                par.paragraph_format.left_indent = Cm(1.2)
                par.paragraph_format.first_line_indent = Cm(-0.6)
                par.paragraph_format.tab_stops.add_tab_stop(Cm(1.2))
                valor = "•\t" + valor[2:]
            _times(par.add_run(valor))
    for j, ancho in enumerate((Cm(5.6), Cm(10.4))):
        t.columns[j].width = ancho
    doc.add_page_break()


caratula()

# ---------------------------------------------------------------------------
# 1. Tema del proyecto
# ---------------------------------------------------------------------------
titulo1("1. Tema del proyecto")

titulo2("1.1 Tema seleccionado")
parrafo("El proyecto analiza la puntualidad de los vuelos comerciales nacionales de Estados Unidos durante el año 2015. Se estudian los retrasos, las cancelaciones y los desvíos de los vuelos según la aerolínea, el aeropuerto, la ruta, la fecha y la hora de salida.")

titulo2("1.2 Conjunto de datos")
parrafo("Los datos se obtuvieron de Kaggle, del conjunto de datos \"2015 Flight Delays and Cancellations\", publicado por el Departamento de Transporte de los Estados Unidos con información de la Oficina de Estadísticas de Transporte (BTS).")
parrafo("Enlace: https://www.kaggle.com/datasets/usdot/flight-delays")
parrafo("El conjunto de datos está formado por tres archivos CSV, que se describen en la Tabla 1.")
tabla("Archivos del conjunto de datos", ["Archivo", "Contenido", "Registros"], [
    ["flights.csv", "Un registro por vuelo con la fecha, la aerolínea, el número de vuelo, los aeropuertos de origen y destino, los horarios, los retrasos, los tiempos de vuelo, la distancia, la cancelación, el desvío y las causas del retraso.", "Más de 5,8 millones"],
    ["airlines.csv", "Código y nombre de cada aerolínea.", "14"],
    ["airports.csv", "Código, nombre, ciudad, estado, país y coordenadas de cada aeropuerto.", "322"],
], [3.2, 9.8, 3.0])
parrafo("La información es suficiente para construir un Data Warehouse. Cada vuelo es un hecho que se puede medir (minutos de retraso, tiempos y distancia) y tiene datos descriptivos que sirven como dimensiones, como la fecha, la aerolínea y los aeropuertos. Estas dimensiones tienen jerarquías naturales: las fechas se agrupan en meses, trimestres y años, y los aeropuertos en ciudades, estados y regiones.")

titulo2("1.3 Contexto de los datos y necesidad de análisis")
parrafo("En Estados Unidos, la BTS considera que un vuelo está retrasado cuando llega 15 minutos o más después de la hora programada. En ese caso la aerolínea informa la causa del retraso, que puede ser la propia aerolínea, el clima, el sistema nacional de aviación, la seguridad o la llegada tardía del avión desde un vuelo anterior. Los vuelos cancelados también tienen registrado el motivo de la cancelación.")
parrafo("Actualmente estos datos están en un archivo plano, que sirve para registrar los vuelos pero no para analizarlos. Por ejemplo, para saber qué aerolínea tuvo más retrasos en diciembre o cuál fue la causa más frecuente, habría que procesar millones de filas en cada consulta. La necesidad de análisis es conocer dónde, cuándo y por qué se producen los retrasos y las cancelaciones, para que las aerolíneas y los aeropuertos puedan mejorar su puntualidad y los pasajeros puedan elegir mejor sus vuelos.")

# ---------------------------------------------------------------------------
# 2. Objetivos
# ---------------------------------------------------------------------------
titulo1("2. Objetivos del Data Warehouse")

titulo2("2.1 Objetivo general")
parrafo("Diseñar e implementar un Data Warehouse que integre los datos de los vuelos nacionales de Estados Unidos del año 2015, para analizar la puntualidad, los retrasos y las cancelaciones por aerolínea, aeropuerto, ruta y período mediante indicadores, reportes y cuadros de mando.")

titulo2("2.2 Objetivos específicos")
parrafo("Los objetivos específicos se presentan en la Tabla 2. Cada uno tiene un indicador que permite medirlo con los datos del DataMart.")
tabla("Objetivos específicos e indicadores", ["N.º", "Objetivo específico", "Indicador"], [
    ["OE1", "Medir la puntualidad de cada aerolínea por mes.", "Porcentaje de vuelos que llegan con menos de 15 minutos de retraso."],
    ["OE2", "Cuantificar las cancelaciones y los desvíos por aerolínea y por motivo.", "Porcentaje de vuelos cancelados y desviados."],
    ["OE3", "Identificar las causas que generan más minutos de retraso.", "Porcentaje de minutos de retraso de cada causa."],
    ["OE4", "Determinar las rutas y los aeropuertos con mayor retraso.", "Promedio de minutos de retraso en la llegada."],
    ["OE5", "Analizar los retrasos según la hora de salida y el día de la semana.", "Promedio de minutos de retraso en la salida."],
    ["OE6", "Evaluar el tiempo que los aviones pasan en tierra en cada aeropuerto.", "Promedio de minutos de rodaje antes del despegue."],
], [1.4, 7.6, 7.0])

titulo2("2.3 Relación de los objetivos con el diseño")
parrafo("A partir de estos objetivos se definió el diseño del DataMart. Todos se responden analizando vuelos, por lo que el hecho principal es el vuelo y la granularidad es un vuelo. Las dimensiones necesarias son la fecha, la hora de salida, la aerolínea, el aeropuerto y el motivo de cancelación. Las métricas son los minutos de retraso, los tiempos de vuelo, la distancia y los indicadores de vuelo cancelado, desviado, retrasado o puntual.")
parrafo("En la segunda presentación cada objetivo tendrá un reporte, y los indicadores principales se reunirán en un cuadro de mando de puntualidad con filtros por aerolínea, aeropuerto y mes.")

# ---------------------------------------------------------------------------
# 3. Modelado conceptual
# ---------------------------------------------------------------------------
titulo1("3. Modelado conceptual del DataMart")

titulo2("3.1 DataMarts propuestos")
parrafo("Con los datos disponibles se identificaron tres posibles DataMarts, que se muestran en la Tabla 3.")
tabla("DataMarts propuestos", ["DataMart", "Qué analiza", "Cada registro representa"], [
    ["Puntualidad de Vuelos", "La operación de cada vuelo: retrasos, cancelaciones y desvíos.", "Un vuelo."],
    ["Causas de Retraso", "Cómo se reparten los minutos de retraso entre sus causas.", "Un vuelo retrasado y una de sus causas."],
    ["Operaciones Aeroportuarias", "El movimiento diario de cada aeropuerto: salidas, llegadas y cancelaciones.", "Un aeropuerto en un día."],
], [4.4, 7.0, 4.6])

titulo2("3.2 DataMart seleccionado")
parrafo("Se eligió el DataMart de Puntualidad de Vuelos porque es el que aporta más valor: guarda el detalle de cada vuelo, permite responder los seis objetivos y los otros dos DataMarts se pueden obtener a partir de él, resumiendo sus datos por causa o por aeropuerto y día.")

titulo2("3.3 Modelo conceptual")
parrafo("El proceso de negocio es la operación de un vuelo programado. El hecho es el vuelo y se describe con seis dimensiones: la fecha, la hora de salida, la aerolínea, el aeropuerto de origen, el aeropuerto de destino y el motivo de cancelación. Los aeropuertos de origen y de destino son la misma dimensión usada en dos roles. La Figura 1 muestra el modelo con las jerarquías de cada dimensión.")

titulo2("3.4 Granularidad")
parrafo("Cada registro de la tabla de hechos representa un vuelo programado de una aerolínea en una fecha, es decir, una fila del archivo flights.csv. Un vuelo se identifica por su fecha, la aerolínea, el número de vuelo, el aeropuerto de origen y la hora programada de salida. Con esta granularidad, la tabla de hechos tendrá más de 5,8 millones de registros.")
figura(diagramas.exportar_png("conceptual"), Cm(14.5), "Modelo conceptual del DataMart Puntualidad de Vuelos.")

# ---------------------------------------------------------------------------
# 4. Modelado lógico
# ---------------------------------------------------------------------------
titulo1("4. Modelado lógico del DataMart")

titulo2("4.1 Tablas de hechos y dimensiones")
parrafo("El modelo lógico es un esquema en estrella formado por una tabla de hechos y cinco tablas de dimensiones. La Tabla 4 detalla los atributos de cada tabla y la Figura 2, al final de este punto, muestra el diagrama del modelo.")
tabla("Tablas del modelo lógico", ["Tabla", "Atributos"], [
    ["fact_vuelo (hechos)", "sk_vuelo (PK); sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino, sk_motivo_cancelacion (FK); numero_vuelo, matricula_avion, salida_programada; retraso_salida_min, retraso_llegada_min, taxi_salida_min, taxi_llegada_min, tiempo_programado_min, tiempo_real_min, tiempo_aire_min, distancia_millas; retraso_aerolinea_min, retraso_clima_min, retraso_sistema_aereo_min, retraso_seguridad_min, retraso_avion_tardio_min; es_cancelado, es_desviado, es_retrasado, es_puntual; fecha_carga"],
    ["dim_fecha", "sk_fecha (PK), fecha, dia, dia_semana, nombre_dia, es_fin_de_semana, mes, nombre_mes, trimestre, anio"],
    ["dim_hora", "sk_hora (PK), hora_texto, franja_horaria"],
    ["dim_aerolinea", "sk_aerolinea (PK), codigo_iata, nombre_aerolinea"],
    ["dim_aeropuerto", "sk_aeropuerto (PK), codigo_iata, nombre_aeropuerto, ciudad, estado, region, pais, latitud, longitud"],
    ["dim_motivo_\u200bcancelacion", "sk_motivo_cancelacion (PK), codigo_motivo, descripcion"],
], [4.3, 11.7])

titulo2("4.2 Claves y relaciones")
parrafo("Cada dimensión tiene una clave sustituta (sk), que es un número generado por la base de datos y funciona como clave primaria. La tabla de hechos guarda una clave foránea hacia cada dimensión, y todas las relaciones son de uno a muchos: por ejemplo, una aerolínea tiene muchos vuelos, pero cada vuelo pertenece a una sola aerolínea.")
parrafo("Los códigos que vienen en los archivos, como el código IATA de aerolíneas y aeropuertos, se guardan como claves naturales y sirven para encontrar la clave sustituta durante la carga. La dimensión aeropuerto se relaciona dos veces con la tabla de hechos, una como origen y otra como destino. El número de vuelo, la matrícula del avión y la hora programada se guardan en la tabla de hechos como dimensiones degeneradas, porque no necesitan una tabla propia.")

titulo2("4.3 Origen de los datos")
parrafo("La Tabla 5 muestra cómo se usa cada columna de los archivos CSV en el DataMart.")
tabla("Columnas del conjunto de datos y su uso en el DataMart", ["Columna del dataset", "Significado", "En el DataMart"], [
    ["YEAR\nMONTH\nDAY\nDAY_OF_WEEK", "Fecha del vuelo y día de la semana", "dim_fecha (dimensión)"],
    ["AIRLINE", "Código de la aerolínea", "dim_aerolinea (dimensión)"],
    ["ORIGIN_AIRPORT\nDESTINATION_AIRPORT", "Aeropuertos de origen y destino", "dim_aeropuerto (dimensión)"],
    ["SCHEDULED_DEPARTURE", "Hora programada de salida", "salida_programada (dimensión degenerada)\ndim_hora (dimensión)"],
    ["CANCELLATION_REASON", "Motivo de la cancelación", "dim_motivo_cancelacion (dimensión)"],
    ["FLIGHT_NUMBER\nTAIL_NUMBER", "Número de vuelo y matrícula del avión", "numero_vuelo\nmatricula_avion\n(dimensiones degeneradas)"],
    ["DEPARTURE_DELAY", "Minutos de retraso en la salida", "retraso_salida_min (métrica)"],
    ["ARRIVAL_DELAY", "Minutos de retraso en la llegada", "retraso_llegada_min (métrica)\nes_retrasado y es_puntual (indicadores)"],
    ["TAXI_OUT\nTAXI_IN", "Minutos de rodaje antes del despegue y después del aterrizaje", "taxi_salida_min\ntaxi_llegada_min\n(métricas)"],
    ["SCHEDULED_TIME\nELAPSED_TIME\nAIR_TIME", "Duración programada, real y en el aire", "tiempo_programado_min\ntiempo_real_min\ntiempo_aire_min\n(métricas)"],
    ["DISTANCE", "Distancia en millas", "distancia_millas (métrica)"],
    ["AIRLINE_DELAY\nWEATHER_DELAY\nAIR_SYSTEM_DELAY\nSECURITY_DELAY\nLATE_AIRCRAFT_DELAY", "Minutos de retraso por cada causa", "retraso_aerolinea_min\nretraso_clima_min\nretraso_sistema_aereo_min\nretraso_seguridad_min\nretraso_avion_tardio_min\n(métricas)"],
    ["CANCELLED\nDIVERTED", "Indican si el vuelo fue cancelado o desviado", "es_cancelado\nes_desviado\n(indicadores)"],
    ["DEPARTURE_TIME\nWHEELS_OFF\nWHEELS_ON\nSCHEDULED_ARRIVAL\nARRIVAL_TIME", "Horas reales y programadas de cada etapa del vuelo", "No se cargan, porque lo necesario ya está en los retrasos y los tiempos"],
    ["airlines.csv (todas)", "Datos de cada aerolínea", "dim_aerolinea (dimensión)"],
    ["airports.csv (todas)", "Datos de cada aeropuerto", "dim_aeropuerto (dimensión); la región se obtiene del estado"],
], [5.9, 4.3, 5.8])

titulo2("4.4 Métricas y su clasificación")
parrafo("En la Tabla 6 se clasifican las métricas de la tabla de hechos según si se pueden sumar o no.")
tabla("Clasificación de las métricas", ["Métrica", "Tipo", "Motivo"], [
    ["Minutos de retraso en la salida y en la llegada", "Aditiva", "Se suman por aerolínea, aeropuerto o fecha para obtener el total de minutos de retraso."],
    ["Minutos de retraso por causa", "Aditiva", "La suma por causa muestra cuál genera más retraso."],
    ["Tiempos de rodaje, tiempo programado, tiempo real y tiempo en el aire", "Aditiva", "Se pueden sumar o promediar por cualquier dimensión."],
    ["Distancia", "Aditiva", "La suma da el total de millas voladas."],
    ["Indicadores de vuelo cancelado, desviado, retrasado y puntual (0 o 1)", "Aditiva", "La suma da la cantidad de vuelos de cada tipo."],
    ["Porcentajes de puntualidad y de cancelación, y promedios", "No aditiva", "No se pueden sumar; se calculan a partir de los totales."],
], [6.2, 2.6, 7.2])
parrafo("No hay métricas semiaditivas, porque cada vuelo es un evento independiente y ninguna medida representa un saldo acumulado en el tiempo.")

titulo2("4.5 Verificación del modelo con los objetivos")
parrafo("La Tabla 7 muestra qué métricas y dimensiones se usan para responder cada objetivo específico.")
tabla("Verificación del modelo lógico", ["Objetivo", "Métricas", "Dimensiones"], [
    ["OE1", "es_puntual, es_retrasado", "Aerolínea y fecha (mes)"],
    ["OE2", "es_cancelado, es_desviado", "Aerolínea y motivo de cancelación"],
    ["OE3", "Minutos de retraso por causa", "Fecha y aerolínea"],
    ["OE4", "retraso_llegada_min", "Aeropuerto de origen y de destino"],
    ["OE5", "retraso_salida_min, es_retrasado", "Hora (franja horaria) y fecha (día de la semana)"],
    ["OE6", "taxi_salida_min", "Aeropuerto de origen"],
], [2.4, 6.6, 7.0])
parrafo("Como se observa, todos los objetivos se pueden responder con las métricas y dimensiones del modelo.")

nueva_seccion(horizontal=True)
figura(diagramas.exportar_png("logico"), Cm(26.5), "Modelo lógico del DataMart Puntualidad de Vuelos.",
       "PK: clave primaria. FK: clave foránea. NK: clave natural. DD: dimensión degenerada. Todas las relaciones son de uno a muchos.")
nueva_seccion(horizontal=False)

# ---------------------------------------------------------------------------
# 5. Modelado físico
# ---------------------------------------------------------------------------
titulo1("5. Modelado físico del DataMart")

titulo2("5.1 Implementación en PostgreSQL")
parrafo("El modelo físico se implementó en PostgreSQL 16, en una base de datos llamada dw_vuelos. Se crearon las cinco tablas de dimensiones y la tabla de hechos con sus tipos de datos, claves, restricciones e índices. También se cargaron los datos fijos: el calendario de 2014 a 2016, las 24 horas del día y los motivos de cancelación. La Figura 3 muestra el modelo físico tal como quedó en la base de datos.")

titulo2("5.2 Tipos de datos y restricciones")
parrafo("La Tabla 8 resume los tipos de datos elegidos para las columnas de las tablas.")
tabla("Tipos de datos utilizados", ["Datos", "Tipo de dato", "Motivo"], [
    ["Claves sustitutas", "INTEGER y BIGINT con IDENTITY", "Se generan automáticamente."],
    ["Minutos, distancia e indicadores", "SMALLINT", "Son números pequeños y los indicadores se pueden sumar."],
    ["Fecha y hora programada", "DATE y TIME", "Permiten trabajar con fechas y horas."],
    ["Códigos y nombres", "VARCHAR y CHAR", "Texto de longitud limitada."],
], [5.0, 5.0, 6.0])
parrafo("Las restricciones definidas son: clave primaria en todas las tablas, UNIQUE en los códigos IATA y en la combinación que identifica a cada vuelo, NOT NULL en las columnas obligatorias y reglas CHECK, por ejemplo, que la distancia sea mayor que cero o que un vuelo cancelado tenga un motivo de cancelación.")

titulo2("5.3 Relaciones e integridad referencial")
parrafo("Las relaciones entre la tabla de hechos y las dimensiones se crearon como claves foráneas: seis en total, dos de ellas hacia la dimensión aeropuerto. Para comprobar la integridad referencial se hicieron pruebas, y la base de datos rechazó correctamente un vuelo con una aerolínea que no existe, un vuelo cancelado sin motivo, un vuelo repetido, una distancia negativa y la eliminación de un aeropuerto que tiene vuelos registrados.")

titulo2("5.4 Preparación para las consultas y para el ETL")
parrafo("Para que las consultas sean rápidas se crearon índices sobre las claves foráneas, sobre la combinación de aerolínea y fecha, sobre las rutas (origen y destino) y un índice parcial para los vuelos cancelados. Para facilitar la carga con Apache Hop, las dimensiones de aerolínea y aeropuerto tienen un registro \"Desconocido\" con clave -\u20601, que se usa cuando un código no se encuentra, y la clave del vuelo evita que se carguen vuelos repetidos si el proceso se ejecuta más de una vez.")

nueva_seccion(horizontal=True)
figura(diagramas.exportar_png("fisico"), Cm(26.5), "Modelo físico del DataMart Puntualidad de Vuelos en PostgreSQL 16.",
       "PK: clave primaria. FK: clave foránea. UK: restricción UNIQUE. NN: NOT NULL. IDENTITY: valor generado por la base de datos.")

doc.save(SALIDA_DOCX)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SALIDA_DOCX.parent), str(SALIDA_DOCX)],
               check=True, capture_output=True)
print("Generados:", SALIDA_DOCX.name, "y", SALIDA_DOCX.with_suffix(".pdf").name)

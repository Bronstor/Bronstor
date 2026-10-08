"""Especificación del modelo dimensional del DataMart "Rendimiento en Carrera".

Es la única fuente para el diccionario de datos y los diagramas del informe;
debe coincidir con sql/01_crear_esquema_y_tablas.sql.
Cada columna: (nombre, tipo, clave, admite_nulo, descripción, origen o regla ETL).
Claves: PK primaria, FK foránea, NK natural (única), DD dimensión degenerada.
"""

TABLAS = {
    "dim_tiempo": {
        "titulo": "Dimensión Tiempo",
        "descripcion": "Calendario diario de 1950 a 2030, generado por SQL antes del ETL. "
                       "Permite agregar los resultados por mes, trimestre, año y década.",
        "columnas": [
            ("sk_tiempo", "INTEGER", "PK", False, "Clave sustituta inteligente con formato AAAAMMDD", "Calculada a partir de la fecha"),
            ("fecha", "DATE", "NK", False, "Fecha calendario", "generate_series 1950-01-01 a 2030-12-31"),
            ("dia", "SMALLINT", "", False, "Día del mes (1-31)", "EXTRACT(DAY)"),
            ("dia_semana", "SMALLINT", "", False, "Día de la semana ISO (1 = lunes, 7 = domingo)", "EXTRACT(ISODOW)"),
            ("nombre_dia", "VARCHAR(10)", "", False, "Nombre del día en español", "Derivado"),
            ("mes", "SMALLINT", "", False, "Mes (1-12)", "EXTRACT(MONTH)"),
            ("nombre_mes", "VARCHAR(10)", "", False, "Nombre del mes en español", "Derivado"),
            ("trimestre", "SMALLINT", "", False, "Trimestre (1-4)", "EXTRACT(QUARTER)"),
            ("semestre", "SMALLINT", "", False, "Semestre (1-2)", "Derivado"),
            ("anio", "SMALLINT", "", False, "Año calendario (coincide con la temporada)", "EXTRACT(YEAR)"),
            ("decada", "SMALLINT", "", False, "Primer año de la década (1950, 1960, ...)", "anio - anio % 10"),
            ("nombre_decada", "VARCHAR(15)", "", False, "Etiqueta de la década, p. ej. «Década de 1990»", "Derivado"),
        ],
    },
    "dim_carrera": {
        "titulo": "Dimensión Carrera (Gran Premio)",
        "descripcion": "Un registro por Gran Premio del campeonato. Agrupa las carreras por temporada "
                       "y conserva el sistema de puntuación vigente para interpretar los puntos.",
        "columnas": [
            ("sk_carrera", "INTEGER", "PK", False, "Clave sustituta (IDENTITY)", "Generada por el DBMS"),
            ("id_carrera_origen", "INTEGER", "NK", False, "Identificador de la carrera en la fuente", "races.raceId"),
            ("temporada", "SMALLINT", "", False, "Año de la temporada (única junto con ronda)", "races.year"),
            ("ronda", "SMALLINT", "", False, "Número de la carrera dentro de la temporada", "races.round"),
            ("total_rondas_temporada", "SMALLINT", "", False, "Cantidad de carreras de la temporada", "MAX(round) por year"),
            ("nombre_gran_premio", "VARCHAR(100)", "", False, "Nombre oficial del Gran Premio", "races.name"),
            ("hora_inicio_utc", "TIME", "", True, "Hora de largada en UTC", "races.time (\\N → NULL)"),
            ("tiene_sprint", "BOOLEAN", "", False, "Indica si el fin de semana tuvo carrera sprint", "Existe en sprint_results"),
            ("sistema_puntos", "VARCHAR(60)", "", False, "Sistema de puntuación vigente en la temporada", "Regla por año (sección 5.7)"),
            ("url_referencia", "VARCHAR(255)", "", True, "Enlace a la página de Wikipedia de la carrera", "races.url"),
        ],
    },
    "dim_circuito": {
        "titulo": "Dimensión Circuito",
        "descripcion": "Circuitos donde se disputaron los Grandes Premios, con su jerarquía geográfica.",
        "columnas": [
            ("sk_circuito", "INTEGER", "PK", False, "Clave sustituta (IDENTITY); -1 = desconocido", "Generada por el DBMS"),
            ("id_circuito_origen", "INTEGER", "NK", False, "Identificador del circuito en la fuente", "circuits.circuitId"),
            ("referencia", "VARCHAR(50)", "", False, "Código corto del circuito", "circuits.circuitRef"),
            ("nombre_circuito", "VARCHAR(100)", "", False, "Nombre del circuito", "circuits.name"),
            ("localidad", "VARCHAR(100)", "", False, "Ciudad o localidad", "circuits.location"),
            ("pais", "VARCHAR(60)", "", False, "País sede", "circuits.country"),
            ("continente", "VARCHAR(20)", "", False, "Continente del país sede", "Tabla de correspondencia país → continente"),
            ("latitud", "NUMERIC(9,6)", "", True, "Latitud geográfica", "circuits.lat"),
            ("longitud", "NUMERIC(9,6)", "", True, "Longitud geográfica", "circuits.lng"),
            ("altitud_m", "INTEGER", "", True, "Altitud sobre el nivel del mar en metros", "circuits.alt (\\N → NULL)"),
        ],
    },
    "dim_piloto": {
        "titulo": "Dimensión Piloto",
        "descripcion": "Pilotos que participaron en al menos un Gran Premio. Cambios lentos de tipo 1 "
                       "(una corrección sobrescribe el valor anterior).",
        "columnas": [
            ("sk_piloto", "INTEGER", "PK", False, "Clave sustituta (IDENTITY); -1 = desconocido", "Generada por el DBMS"),
            ("id_piloto_origen", "INTEGER", "NK", False, "Identificador del piloto en la fuente", "drivers.driverId"),
            ("referencia", "VARCHAR(50)", "", False, "Código corto del piloto", "drivers.driverRef"),
            ("codigo", "CHAR(3)", "", True, "Código de tres letras (VER, HAM, ...)", "drivers.code (\\N → NULL)"),
            ("numero_permanente", "SMALLINT", "", True, "Número permanente (desde 2014)", "drivers.number (\\N → NULL)"),
            ("nombre", "VARCHAR(60)", "", False, "Nombre de pila", "drivers.forename"),
            ("apellido", "VARCHAR(60)", "", False, "Apellido", "drivers.surname"),
            ("nombre_completo", "VARCHAR(120)", "", False, "Nombre y apellido para reportes", "forename || ' ' || surname"),
            ("fecha_nacimiento", "DATE", "", True, "Fecha de nacimiento", "drivers.dob"),
            ("nacionalidad", "VARCHAR(50)", "", False, "Nacionalidad deportiva", "drivers.nationality"),
        ],
    },
    "dim_escuderia": {
        "titulo": "Dimensión Escudería",
        "descripcion": "Constructores o equipos. En la fuente, un cambio de nombre comercial "
                       "(p. ej. Toro Rosso → AlphaTauri) ya aparece como otro constructor, por lo que basta el tipo 1.",
        "columnas": [
            ("sk_escuderia", "INTEGER", "PK", False, "Clave sustituta (IDENTITY); -1 = desconocida", "Generada por el DBMS"),
            ("id_escuderia_origen", "INTEGER", "NK", False, "Identificador del constructor en la fuente", "constructors.constructorId"),
            ("referencia", "VARCHAR(50)", "", False, "Código corto del constructor", "constructors.constructorRef"),
            ("nombre_escuderia", "VARCHAR(100)", "", False, "Nombre de la escudería", "constructors.name"),
            ("nacionalidad", "VARCHAR(50)", "", False, "Nacionalidad de la escudería", "constructors.nationality"),
        ],
    },
    "dim_estado": {
        "titulo": "Dimensión Estado de finalización",
        "descripcion": "Estado con el que el piloto terminó la carrera, agrupado en categorías de análisis.",
        "columnas": [
            ("sk_estado", "INTEGER", "PK", False, "Clave sustituta (IDENTITY); -1 = desconocido", "Generada por el DBMS"),
            ("id_estado_origen", "INTEGER", "NK", False, "Identificador del estado en la fuente", "status.statusId"),
            ("descripcion_estado", "VARCHAR(60)", "", False, "Estado original (Finished, +1 Lap, Engine, ...)", "status.status"),
            ("categoria_estado", "VARCHAR(40)", "", False, "Categoría de análisis del estado", "Regla de agrupación (sección 5.7)"),
        ],
    },
    "fact_resultado_carrera": {
        "titulo": "Tabla de hechos Resultado de carrera",
        "descripcion": "Un registro por cada resultado de un piloto con un auto en un Gran Premio.",
        "columnas": [
            ("sk_resultado", "BIGINT", "PK", False, "Clave sustituta del hecho (IDENTITY)", "Generada por el DBMS"),
            ("sk_tiempo", "INTEGER", "FK", False, "Fecha de la carrera", "races.date → dim_tiempo"),
            ("sk_carrera", "INTEGER", "FK", False, "Gran Premio", "results.raceId → dim_carrera"),
            ("sk_circuito", "INTEGER", "FK", False, "Circuito de la carrera", "races.circuitId → dim_circuito"),
            ("sk_piloto", "INTEGER", "FK", False, "Piloto", "results.driverId → dim_piloto"),
            ("sk_escuderia", "INTEGER", "FK", False, "Escudería con la que corrió", "results.constructorId → dim_escuderia"),
            ("sk_estado", "INTEGER", "FK", False, "Estado de finalización", "results.statusId → dim_estado"),
            ("id_resultado_origen", "INTEGER", "DD", False, "Identificador del resultado (único)", "results.resultId"),
            ("numero_auto", "SMALLINT", "DD", True, "Número del auto en la carrera", "results.number"),
            ("codigo_posicion", "VARCHAR(3)", "DD", False, "Posición oficial o código R, D, E, W, F, N", "results.positionText"),
            ("posicion_salida", "SMALLINT", "", False, "Posición de largada (0 = desde boxes)", "results.grid"),
            ("posicion_final", "SMALLINT", "", True, "Posición clasificada; nula si no fue clasificado", "results.position"),
            ("orden_llegada", "SMALLINT", "", False, "Orden final de todos los participantes", "results.positionOrder"),
            ("posiciones_ganadas", "SMALLINT", "", True, "Posiciones ganadas (negativo = perdidas)", "grid − position (si grid > 0 y clasificado)"),
            ("puntos", "NUMERIC(5,2)", "", False, "Puntos oficiales del Gran Premio", "results.points"),
            ("puntos_sistema_actual", "NUMERIC(5,2)", "", False, "Puntos recalculados con el sistema actual", "25-18-15-12-10-8-6-4-2-1 según position"),
            ("vueltas_completadas", "SMALLINT", "", False, "Vueltas completadas", "results.laps"),
            ("tiempo_carrera_ms", "BIGINT", "", True, "Tiempo total de carrera en milisegundos", "results.milliseconds"),
            ("tiempo_vuelta_rapida_ms", "INTEGER", "", True, "Mejor vuelta del piloto en milisegundos", "results.fastestLapTime (m:ss.mmm → ms)"),
            ("velocidad_vuelta_rapida_kmh", "NUMERIC(7,3)", "", True, "Velocidad media de la mejor vuelta (km/h)", "results.fastestLapSpeed"),
            ("ranking_vuelta_rapida", "SMALLINT", "", True, "Puesto de su mejor vuelta en la carrera", "results.rank"),
            ("edad_piloto", "NUMERIC(4,1)", "", True, "Edad del piloto el día de la carrera (años)", "(races.date − drivers.dob) / 365,25"),
            ("puntos_acumulados_temporada", "NUMERIC(6,2)", "", True, "Puntos del piloto en el campeonato tras la carrera", "driver_standings.points"),
            ("posicion_campeonato", "SMALLINT", "", True, "Posición del piloto en el campeonato tras la carrera", "driver_standings.position"),
            ("es_victoria", "SMALLINT", "", False, "1 si ganó la carrera", "posicion_final = 1"),
            ("es_podio", "SMALLINT", "", False, "1 si terminó entre los tres primeros", "posicion_final ≤ 3"),
            ("es_pole", "SMALLINT", "", False, "1 si largó primero", "posicion_salida = 1"),
            ("es_en_puntos", "SMALLINT", "", False, "1 si sumó puntos", "puntos > 0"),
            ("es_vuelta_rapida", "SMALLINT", "", False, "1 si hizo la vuelta más rápida de la carrera", "ranking_vuelta_rapida = 1"),
            ("es_finalizado", "SMALLINT", "", False, "1 si fue clasificado", "posicion_final no nula"),
            ("es_abandono", "SMALLINT", "", False, "1 si se retiró sin ser clasificado", "codigo_posicion = 'R'"),
            ("fecha_carga", "TIMESTAMP", "", False, "Fecha y hora de carga (auditoría del ETL)", "DEFAULT CURRENT_TIMESTAMP"),
        ],
    },
}

# Jerarquías de cada dimensión (de lo general a lo particular)
JERARQUIAS = {
    "dim_tiempo": ("Tiempo", ["Década", "Año", "Semestre", "Trimestre", "Mes", "Fecha"]),
    "dim_carrera": ("Carrera", ["Temporada", "Gran Premio"]),
    "dim_circuito": ("Circuito", ["Continente", "País", "Localidad", "Circuito"]),
    "dim_piloto": ("Piloto", ["Nacionalidad", "Piloto"]),
    "dim_escuderia": ("Escudería", ["Nacionalidad", "Escudería"]),
    "dim_estado": ("Estado", ["Categoría", "Estado"]),
}

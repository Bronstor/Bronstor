# Data Warehouse de puntualidad de vuelos en EE. UU. (2015)

Proyecto de **Base de Datos III**: implementación de un Data Warehouse a partir del
dataset público [2015 Flight Delays and Cancellations](https://www.kaggle.com/datasets/usdot/flight-delays)
de Kaggle (Departamento de Transporte de EE. UU.).

## Primera presentación (puntos 1 a 5)

- [`docs/Primera_Presentacion_DW_Vuelos.pdf`](docs/Primera_Presentacion_DW_Vuelos.pdf): entrega en PDF, en Arial 12, con los diagramas de los modelos conceptual (Figura 1), lógico (Figura 2) y físico (Figura 3) y el script SQL como anexo.
- [`docs/Primera_Presentacion_DW_Vuelos.docx`](docs/Primera_Presentacion_DW_Vuelos.docx): el mismo documento en Word, para completar el encabezado y exportar a PDF.

El documento sigue los puntos 1 a 5 de la consigna: tema y dataset, objetivos,
modelo conceptual (tres DataMarts, selección y granularidad), modelo lógico (tablas,
claves, métricas y verificación) y modelo físico en PostgreSQL 16.

## Modelo

Esquema en estrella del DataMart **Puntualidad de Vuelos**:

| Tabla | Contenido |
|-------|-----------|
| `fact_vuelo` | Un vuelo programado de una aerolínea en una fecha (grano) |
| `dim_fecha` | Calendario 2014-2016 (Año > Trimestre > Mes > Fecha; día de la semana) |
| `dim_hora` | Hora programada de salida (Franja horaria > Hora) |
| `dim_aerolinea` | Aerolíneas |
| `dim_aeropuerto` | Aeropuertos (Región > Estado > Ciudad > Aeropuerto); se usa como origen y como destino |
| `dim_motivo_cancelacion` | No cancelado, aerolínea, clima, sistema aéreo, seguridad |

## Cómo crear la base de datos

Requiere PostgreSQL 16 (o superior). Desde la carpeta `sql/`:

```bash
createdb -U postgres -E UTF8 -T template0 dw_vuelos
psql -U postgres -d dw_vuelos -f 01_crear_esquema_y_tablas.sql
psql -U postgres -d dw_vuelos -f 02_crear_indices.sql
psql -U postgres -d dw_vuelos -f 03_datos_iniciales.sql
psql -U postgres -d dw_vuelos -f 05_pruebas_integridad.sql   # opcional: pruebas con ROLLBACK
```

`04_consultas_objetivos.sql` contiene una consulta analítica por objetivo; devolverá
resultados reales después de la carga ETL (segunda presentación).

## Estructura

```
proyecto-dw-vuelos/
├── sql/                     Scripts del modelo físico (01 a 05)
└── docs/
    ├── Primera_Presentacion_DW_Vuelos.pdf
    ├── Primera_Presentacion_DW_Vuelos.docx
    └── fuente/
        ├── construir_docx.py    Genera el .docx y el .pdf
        ├── diagramas.py         Dibuja los diagramas conceptual, lógico y físico
        ├── capturar_svg.js      Convierte el diagrama a PNG (Chromium)
        └── modelo_fisico.json   Tablas, columnas y tipos tomados del catálogo de PostgreSQL
```

## Regenerar el documento

Lo más simple para completar el encabezado (universidad, integrantes) es editar el
`.docx` en Word y exportarlo a PDF. Para regenerarlo desde la fuente:

```bash
cd docs/fuente
NODE_PATH=$(npm root -g) python3 construir_docx.py
```

Requiere Python 3 con `python-docx`, LibreOffice (`soffice`) para exportar a PDF y
Node.js con `playwright` (Chromium) para dibujar los diagramas.

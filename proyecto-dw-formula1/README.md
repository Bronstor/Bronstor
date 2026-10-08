# Data Warehouse del Campeonato Mundial de Fórmula 1

Proyecto de **Base de Datos III**: implementación de un Data Warehouse a partir del
dataset público [Formula 1 World Championship (1950 – 2024)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) de Kaggle.

## Primera presentación (puntos 1 a 5)

- [`docs/Primera_Presentacion_DW_Formula1.pdf`](docs/Primera_Presentacion_DW_Formula1.pdf): entrega en PDF (3 páginas, Arial 12).
- [`docs/Primera_Presentacion_DW_Formula1.docx`](docs/Primera_Presentacion_DW_Formula1.docx): el mismo documento en Word, para completar el encabezado y exportar a PDF.

El documento sigue los puntos 1 a 5 de la consigna: tema y dataset, objetivos,
modelo conceptual (tres DataMarts, selección y granularidad), modelo lógico (tablas,
claves, métricas y verificación) y modelo físico en PostgreSQL 16.

## Modelo

Esquema en estrella con una tabla de hechos y seis dimensiones:

| Tabla | Contenido |
|-------|-----------|
| `fact_resultado_carrera` | Resultado de un piloto con un auto en un Gran Premio (grano) |
| `dim_tiempo` | Calendario 1950-2030 (Década > Año > Semestre > Trimestre > Mes > Fecha) |
| `dim_carrera` | Gran Premio (Temporada > Ronda) |
| `dim_circuito` | Circuito (Continente > País > Localidad > Circuito) |
| `dim_piloto` | Piloto (Nacionalidad > Piloto) |
| `dim_escuderia` | Escudería (Nacionalidad > Escudería) |
| `dim_estado` | Estado de finalización (Categoría > Estado) |

## Cómo crear la base de datos

Requiere PostgreSQL 16 (o superior). Desde la carpeta `sql/`:

```bash
createdb -U postgres -E UTF8 -T template0 dw_formula1
psql -U postgres -d dw_formula1 -f 01_crear_esquema_y_tablas.sql
psql -U postgres -d dw_formula1 -f 02_crear_indices.sql
psql -U postgres -d dw_formula1 -f 03_datos_iniciales.sql
psql -U postgres -d dw_formula1 -f 05_pruebas_integridad.sql   # opcional: pruebas con ROLLBACK
```

`04_consultas_objetivos.sql` contiene una consulta analítica por objetivo; devolverá
resultados reales después de la carga ETL (segunda presentación).

## Estructura

```
proyecto-dw-formula1/
├── sql/                     Scripts del modelo físico (01 a 05)
└── docs/
    ├── Primera_Presentacion_DW_Formula1.pdf
    ├── Primera_Presentacion_DW_Formula1.docx
    └── fuente/
        ├── construir_docx.py    Genera el .docx y el .pdf
        └── evidencia/           Salida de PostgreSQL al crear el modelo y probar la integridad
```

## Regenerar el documento

Lo más simple para completar el encabezado (universidad, integrantes) es editar el
`.docx` en Word y exportarlo a PDF. Para regenerarlo desde la fuente:

```bash
cd docs/fuente
python3 construir_docx.py
```

Requiere Python 3 con `python-docx` y LibreOffice (`soffice`) para exportar a PDF.

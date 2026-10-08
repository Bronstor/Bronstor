# Data Warehouse del Campeonato Mundial de Fórmula 1

Proyecto de **Base de Datos III**: implementación de un Data Warehouse a partir del
dataset público [Formula 1 World Championship (1950 – 2024)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) de Kaggle.

## Primera presentación (puntos 1 a 5)

- [`docs/Primera_Presentacion_DW_Formula1.pdf`](docs/Primera_Presentacion_DW_Formula1.pdf): entrega en PDF.
- [`docs/Primera_Presentacion_DW_Formula1.docx`](docs/Primera_Presentacion_DW_Formula1.docx): el mismo documento en Word
  (Arial 12), para completar la carátula y exportar de nuevo a PDF.

El documento sigue la consigna punto por punto; cada viñeta de la consigna es una
sección:

1. **Tema del Proyecto**: tema y dataset de Kaggle; suficiencia de los datos para el análisis, el modelado dimensional y el Data Warehouse; contexto y necesidad de análisis; justificación de la temática.
2. **Objetivos del Data Warehouse**: objetivo general; objetivos específicos medibles con sus indicadores, consultas y reportes; elementos del diseño (hechos, dimensiones, métricas, granularidad, reportes y cuadros de mando) que se derivan de cada objetivo.
3. **Modelado Conceptual**: tres DataMarts propuestos y matriz de bus; selección del de mayor valor (*Rendimiento en Carrera*); modelo conceptual con procesos de negocio, hecho y dimensiones; granularidad de cada hecho.
4. **Modelado Lógico**: tablas de hechos y dimensiones con todos sus atributos; claves primarias, foráneas y sustitutas y relaciones; métricas clasificadas en aditivas, semiaditivas y no aditivas; verificación frente a los objetivos.
5. **Modelado Físico**: implementación en PostgreSQL 16 con tipos de datos, restricciones, claves e índices; relaciones e integridad referencial probadas; estructura orientada a las consultas analíticas y a la carga ETL.

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
    └── fuente/              Generador del documento (python-docx) y diagramas
```

## Regenerar el documento

Lo más simple para cambiar la carátula (universidad, integrantes) es editar el
`.docx` en Word y exportarlo a PDF. Para regenerarlo desde la fuente:

```bash
cd docs/fuente
NODE_PATH=$(npm root -g) python3 construir_docx.py
```

Requiere Python 3 con `python-docx`, LibreOffice (`soffice`, para exportar a PDF) y
Node.js con `playwright` (Chromium, para dibujar los diagramas). El diccionario de
datos y los diagramas se generan a partir de `docs/fuente/modelo.py`, que debe
coincidir con `sql/01_crear_esquema_y_tablas.sql`.

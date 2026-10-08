# Data Warehouse del Campeonato Mundial de Fórmula 1

Proyecto de **Base de Datos III**: implementación de un Data Warehouse a partir del
dataset público [Formula 1 World Championship (1950 – 2024)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) de Kaggle.

## Primera presentación (puntos 1 a 5)

El informe en PDF está en [`docs/Primera_Presentacion_DW_Formula1.pdf`](docs/Primera_Presentacion_DW_Formula1.pdf) y contiene:

1. **Tema del proyecto**: contexto de los datos, necesidad de análisis y observaciones de calidad.
2. **Objetivos del Data Warehouse**: objetivo general, seis objetivos específicos y sus indicadores (KPI).
3. **Modelado conceptual**: tres DataMarts propuestos, matriz de bus, selección del DataMart *Rendimiento en Carrera* y granularidad.
4. **Modelado lógico**: esquema en estrella, diccionario de datos, claves, relaciones y clasificación de métricas.
5. **Modelado físico**: implementación en PostgreSQL 16 con restricciones, índices y evidencia de ejecución.

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
    └── fuente/              Fuente del informe (HTML, diagramas y script de generación)
```

## Regenerar el PDF

Para cambiar la portada (universidad, integrantes) u otro contenido, edita
`docs/fuente/informe.html` y ejecuta:

```bash
cd docs/fuente
NODE_PATH=$(npm root -g) python3 construir_informe.py
```

Requiere Python 3 con `pypdf` y Node.js con `playwright` (Chromium). El diccionario
de datos y los diagramas se generan a partir de `docs/fuente/modelo.py`, que debe
coincidir con `sql/01_crear_esquema_y_tablas.sql`.

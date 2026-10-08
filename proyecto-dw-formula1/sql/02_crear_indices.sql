-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de Fórmula 1
-- Script 02: índices orientados a consultas analíticas
--
-- Las claves primarias y las restricciones UNIQUE sobre las claves
-- naturales (id_*_origen) ya crean sus propios índices; estos últimos
-- son los que usa el ETL para buscar la clave sustituta de cada fila.
-- =====================================================================

SET search_path TO dw_f1;

-- Tabla de hechos: índice por clave foránea (filtros y uniones)
CREATE INDEX ix_fact_resultado_tiempo    ON fact_resultado_carrera (sk_tiempo);
CREATE INDEX ix_fact_resultado_carrera   ON fact_resultado_carrera (sk_carrera);
CREATE INDEX ix_fact_resultado_circuito  ON fact_resultado_carrera (sk_circuito);
CREATE INDEX ix_fact_resultado_estado    ON fact_resultado_carrera (sk_estado);

-- Series de tiempo por piloto y por escudería (evolución por temporada).
-- Como sk_piloto y sk_escuderia son la primera columna, estos índices
-- también cubren los filtros por piloto o por escudería.
CREATE INDEX ix_fact_resultado_piloto_tiempo    ON fact_resultado_carrera (sk_piloto, sk_tiempo);
CREATE INDEX ix_fact_resultado_escuderia_tiempo ON fact_resultado_carrera (sk_escuderia, sk_tiempo);

-- Índice parcial para el análisis de victorias (pocas filas, consultas frecuentes)
CREATE INDEX ix_fact_resultado_victorias ON fact_resultado_carrera (sk_escuderia, sk_piloto)
    WHERE es_victoria = 1;

-- Dimensiones: atributos usados como niveles de jerarquía o filtros
CREATE INDEX ix_dim_tiempo_anio_mes        ON dim_tiempo (anio, mes);
CREATE INDEX ix_dim_tiempo_decada          ON dim_tiempo (decada);
CREATE INDEX ix_dim_carrera_temporada      ON dim_carrera (temporada);
CREATE INDEX ix_dim_circuito_pais          ON dim_circuito (continente, pais);
CREATE INDEX ix_dim_piloto_nacionalidad    ON dim_piloto (nacionalidad);
CREATE INDEX ix_dim_piloto_apellido        ON dim_piloto (apellido);
CREATE INDEX ix_dim_escuderia_nombre       ON dim_escuderia (nombre_escuderia);
CREATE INDEX ix_dim_estado_categoria       ON dim_estado (categoria_estado);

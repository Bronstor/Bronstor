-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de vuelos en EE. UU. (2015)
-- Script 02: índices orientados a consultas analíticas
--
-- Las claves primarias y las restricciones UNIQUE ya crean sus propios
-- índices. La clave natural del vuelo empieza por sk_fecha, por lo que
-- también sirve para filtrar por fecha.
-- =====================================================================

SET search_path TO dw_vuelos;

-- Tabla de hechos: índices por clave foránea (filtros y uniones)
CREATE INDEX ix_fact_vuelo_hora    ON fact_vuelo (sk_hora_salida);
CREATE INDEX ix_fact_vuelo_destino ON fact_vuelo (sk_aeropuerto_destino);
CREATE INDEX ix_fact_vuelo_motivo  ON fact_vuelo (sk_motivo_cancelacion);

-- Combinaciones frecuentes: aerolínea en el tiempo y rutas (origen, destino)
CREATE INDEX ix_fact_vuelo_aerolinea_fecha ON fact_vuelo (sk_aerolinea, sk_fecha);
CREATE INDEX ix_fact_vuelo_ruta            ON fact_vuelo (sk_aeropuerto_origen, sk_aeropuerto_destino);

-- Índice parcial para el análisis de cancelaciones (pocas filas)
CREATE INDEX ix_fact_vuelo_cancelados ON fact_vuelo (sk_aerolinea, sk_motivo_cancelacion)
    WHERE es_cancelado = 1;

-- Dimensiones: atributos usados como niveles de jerarquía o filtros
CREATE INDEX ix_dim_fecha_anio_mes      ON dim_fecha (anio, mes);
CREATE INDEX ix_dim_fecha_dia_semana    ON dim_fecha (dia_semana);
CREATE INDEX ix_dim_hora_franja         ON dim_hora (franja_horaria);
CREATE INDEX ix_dim_aeropuerto_region   ON dim_aeropuerto (region, estado);
CREATE INDEX ix_dim_aeropuerto_ciudad   ON dim_aeropuerto (ciudad);

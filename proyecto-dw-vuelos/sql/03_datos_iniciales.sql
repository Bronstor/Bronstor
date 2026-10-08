-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de vuelos en EE. UU. (2015)
-- Script 03: datos iniciales previos al ETL
--   1. Dimensiones fijas: hora y motivo de cancelación
--   2. Miembros "Desconocido" (clave -1)
--   3. Dimensión fecha (2014-2016)
-- =====================================================================

SET search_path TO dw_vuelos;

-- ---------------------------------------------------------------------
-- 1. Dimensiones fijas
-- ---------------------------------------------------------------------
INSERT INTO dim_hora (sk_hora, hora_texto, franja_horaria)
SELECT h,
       LPAD(h::TEXT, 2, '0') || ':00',
       CASE WHEN h < 6 THEN 'Madrugada'
            WHEN h < 12 THEN 'Mañana'
            WHEN h < 18 THEN 'Tarde'
            ELSE 'Noche' END
FROM generate_series(0, 23) AS g(h);

INSERT INTO dim_motivo_cancelacion (sk_motivo_cancelacion, codigo_motivo, descripcion) VALUES
    (0, 'N', 'No cancelado'),
    (1, 'A', 'Aerolínea'),
    (2, 'B', 'Clima'),
    (3, 'C', 'Sistema Nacional de Aviación'),
    (4, 'D', 'Seguridad');

-- ---------------------------------------------------------------------
-- 2. Miembros desconocidos
-- El ETL asigna la clave -1 cuando un vuelo referencia una aerolínea o
-- un aeropuerto que no existe en la dimensión, en lugar de descartarlo.
-- ---------------------------------------------------------------------
INSERT INTO dim_aerolinea (sk_aerolinea, codigo_iata, nombre_aerolinea)
VALUES (-1, 'UNK', 'Desconocida');

INSERT INTO dim_aeropuerto (sk_aeropuerto, codigo_iata, nombre_aeropuerto, ciudad, estado, region, pais)
VALUES (-1, 'UNK', 'Desconocido', 'Desconocida', 'NA', 'Desconocida', 'Desconocido');

-- ---------------------------------------------------------------------
-- 3. Dimensión fecha: un registro por día
-- ---------------------------------------------------------------------
INSERT INTO dim_fecha (sk_fecha, fecha, dia, dia_semana, nombre_dia, es_fin_de_semana,
                       mes, nombre_mes, trimestre, anio)
SELECT TO_CHAR(d, 'YYYYMMDD')::INTEGER,
       d::DATE,
       EXTRACT(DAY FROM d),
       EXTRACT(ISODOW FROM d),
       (ARRAY['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
           [EXTRACT(ISODOW FROM d)],
       EXTRACT(ISODOW FROM d) >= 6,
       EXTRACT(MONTH FROM d),
       (ARRAY['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
              'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
           [EXTRACT(MONTH FROM d)],
       EXTRACT(QUARTER FROM d),
       EXTRACT(YEAR FROM d)
FROM generate_series(DATE '2014-01-01', DATE '2016-12-31', INTERVAL '1 day') AS g(d);

-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de Fórmula 1
-- Script 03: datos iniciales previos al ETL
--   1. Miembros "Desconocido" (clave -1) para búsquedas sin coincidencia
--   2. Generación completa de la dimensión tiempo (1950-2030)
-- =====================================================================

SET search_path TO dw_f1;

-- ---------------------------------------------------------------------
-- 1. Miembros desconocidos
-- El ETL asigna la clave -1 cuando un resultado referencia un circuito,
-- piloto, escudería o estado que no existe en la dimensión, en lugar de
-- descartar la fila. Un resultado sin carrera válida se rechaza, porque
-- la carrera determina la fecha y el circuito del hecho.
-- ---------------------------------------------------------------------
INSERT INTO dim_circuito (sk_circuito, id_circuito_origen, referencia, nombre_circuito,
                          localidad, pais, continente)
VALUES (-1, -1, 'desconocido', 'Desconocido', 'Desconocida', 'Desconocido', 'Desconocido');

INSERT INTO dim_piloto (sk_piloto, id_piloto_origen, referencia, nombre, apellido,
                        nombre_completo, nacionalidad)
VALUES (-1, -1, 'desconocido', 'Desconocido', 'Desconocido', 'Desconocido', 'Desconocida');

INSERT INTO dim_escuderia (sk_escuderia, id_escuderia_origen, referencia, nombre_escuderia,
                           nacionalidad)
VALUES (-1, -1, 'desconocido', 'Desconocida', 'Desconocida');

INSERT INTO dim_estado (sk_estado, id_estado_origen, descripcion_estado, categoria_estado)
VALUES (-1, -1, 'Desconocido', 'Desconocido');

-- ---------------------------------------------------------------------
-- 2. Dimensión tiempo: un registro por día
-- ---------------------------------------------------------------------
INSERT INTO dim_tiempo (sk_tiempo, fecha, dia, dia_semana, nombre_dia, mes, nombre_mes,
                        trimestre, semestre, anio, decada, nombre_decada)
SELECT TO_CHAR(d, 'YYYYMMDD')::INTEGER,
       d::DATE,
       EXTRACT(DAY FROM d),
       EXTRACT(ISODOW FROM d),
       (ARRAY['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
           [EXTRACT(ISODOW FROM d)],
       EXTRACT(MONTH FROM d),
       (ARRAY['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
              'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
           [EXTRACT(MONTH FROM d)],
       EXTRACT(QUARTER FROM d),
       CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 1 ELSE 2 END,
       EXTRACT(YEAR FROM d),
       EXTRACT(YEAR FROM d)::INTEGER / 10 * 10,
       'Década de ' || (EXTRACT(YEAR FROM d)::INTEGER / 10 * 10)
FROM generate_series(DATE '1950-01-01', DATE '2030-12-31', INTERVAL '1 day') AS g(d);

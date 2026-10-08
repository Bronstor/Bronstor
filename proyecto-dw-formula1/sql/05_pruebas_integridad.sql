-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de Fórmula 1
-- Script 05: pruebas de integridad referencial y de dominio
--
-- Inserta un Gran Premio de ejemplo, intenta cinco operaciones inválidas
-- y deshace todo al final (ROLLBACK). Cada operación inválida debe
-- terminar con ERROR. Ejecutar con psql:
--   psql -U postgres -d dw_formula1 -f 05_pruebas_integridad.sql
-- =====================================================================

\set ON_ERROR_ROLLBACK on
SET search_path TO dw_f1;

BEGIN;

-- Datos de ejemplo (se deshacen al final)
INSERT INTO dim_carrera (sk_carrera, id_carrera_origen, temporada, ronda, total_rondas_temporada,
                         nombre_gran_premio, sistema_puntos)
VALUES (1000, 99001, 2023, 1, 22, 'Gran Premio de prueba', '2019-2024: 25-18-15-12-10-8-6-4-2-1 + 1 vuelta rápida');
INSERT INTO dim_circuito (sk_circuito, id_circuito_origen, referencia, nombre_circuito, localidad, pais, continente)
VALUES (1000, 99001, 'prueba', 'Circuito de prueba', 'Localidad', 'País', 'Asia');
INSERT INTO dim_piloto (sk_piloto, id_piloto_origen, referencia, nombre, apellido, nombre_completo, nacionalidad)
VALUES (1000, 99001, 'prueba', 'Piloto', 'Prueba', 'Piloto Prueba', 'Bolivian');
INSERT INTO dim_escuderia (sk_escuderia, id_escuderia_origen, referencia, nombre_escuderia, nacionalidad)
VALUES (1000, 99001, 'prueba', 'Escudería de prueba', 'Bolivian');
INSERT INTO dim_estado (sk_estado, id_estado_origen, descripcion_estado, categoria_estado)
VALUES (1000, 99001, 'Finished', 'Finalizó');
INSERT INTO fact_resultado_carrera (sk_tiempo, sk_carrera, sk_circuito, sk_piloto, sk_escuderia, sk_estado,
       id_resultado_origen, codigo_posicion, posicion_salida, posicion_final, orden_llegada,
       posiciones_ganadas, puntos, puntos_sistema_actual, vueltas_completadas,
       es_victoria, es_podio, es_pole, es_en_puntos, es_finalizado)
VALUES (20230305, 1000, 1000, 1000, 1000, 1000, 99001, '1', 1, 1, 1, 0, 25, 25, 57, 1, 1, 1, 1, 1);

\echo '--- Prueba 1: clave foránea inexistente (sk_piloto = 9999) -> debe fallar'
INSERT INTO fact_resultado_carrera (sk_tiempo, sk_carrera, sk_circuito, sk_piloto, sk_escuderia, sk_estado,
       id_resultado_origen, codigo_posicion, posicion_salida, posicion_final, orden_llegada, es_finalizado)
VALUES (20230305, 1000, 1000, 9999, 1000, 1000, 99002, '5', 3, 5, 5, 1);

\echo '--- Prueba 2: indicador incoherente (es_victoria = 1 con posicion_final = 2) -> debe fallar'
INSERT INTO fact_resultado_carrera (sk_tiempo, sk_carrera, sk_circuito, sk_piloto, sk_escuderia, sk_estado,
       id_resultado_origen, codigo_posicion, posicion_salida, posicion_final, orden_llegada,
       es_victoria, es_podio, es_finalizado)
VALUES (20230305, 1000, 1000, 1000, 1000, 1000, 99003, '2', 3, 2, 2, 1, 1, 1);

\echo '--- Prueba 3: resultado duplicado (id_resultado_origen repetido) -> debe fallar'
INSERT INTO fact_resultado_carrera (sk_tiempo, sk_carrera, sk_circuito, sk_piloto, sk_escuderia, sk_estado,
       id_resultado_origen, codigo_posicion, posicion_salida, orden_llegada, es_abandono)
VALUES (20230305, 1000, 1000, 1000, 1000, 1000, 99001, 'R', 3, 6, 1);

\echo '--- Prueba 4: borrar un piloto que tiene hechos asociados -> debe fallar'
DELETE FROM dim_piloto WHERE sk_piloto = 1000;

\echo '--- Prueba 5: puntos negativos -> debe fallar'
INSERT INTO fact_resultado_carrera (sk_tiempo, sk_carrera, sk_circuito, sk_piloto, sk_escuderia, sk_estado,
       id_resultado_origen, codigo_posicion, posicion_salida, posicion_final, orden_llegada, puntos, es_finalizado)
VALUES (20230305, 1000, 1000, 1000, 1000, 1000, 99005, '12', 3, 12, 12, -2, 1);

\echo '--- Control: la tabla de hechos conserva solo el registro válido de ejemplo'
SELECT id_resultado_origen, codigo_posicion, puntos, es_victoria
FROM fact_resultado_carrera
WHERE id_resultado_origen BETWEEN 99001 AND 99005;

ROLLBACK;

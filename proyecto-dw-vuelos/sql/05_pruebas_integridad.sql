-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de vuelos en EE. UU. (2015)
-- Script 05: pruebas de integridad referencial y de dominio
--
-- Inserta un vuelo de ejemplo, intenta cinco operaciones inválidas y
-- deshace todo al final (ROLLBACK). Cada operación inválida debe
-- terminar con ERROR. Ejecutar con psql:
--   psql -U postgres -d dw_vuelos -f 05_pruebas_integridad.sql
-- =====================================================================

\set ON_ERROR_ROLLBACK on
SET search_path TO dw_vuelos;

BEGIN;

-- Datos de ejemplo (se deshacen al final)
INSERT INTO dim_aerolinea (sk_aerolinea, codigo_iata, nombre_aerolinea)
VALUES (1000, 'ZZ', 'Aerolínea de prueba');
INSERT INTO dim_aeropuerto (sk_aeropuerto, codigo_iata, nombre_aeropuerto, ciudad, estado, region, pais)
VALUES (1000, 'ZZA', 'Aeropuerto de prueba A', 'Ciudad A', 'TX', 'Sur', 'USA'),
       (1001, 'ZZB', 'Aeropuerto de prueba B', 'Ciudad B', 'CA', 'Oeste', 'USA');
INSERT INTO fact_vuelo (sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino,
       sk_motivo_cancelacion, numero_vuelo, salida_programada, retraso_salida_min, retraso_llegada_min,
       distancia_millas, es_puntual)
VALUES (20150105, 8, 1000, 1000, 1001, 0, 101, '08:15', 3, -2, 1235, 1);

\echo '--- Prueba 1: aerolínea inexistente (sk_aerolinea = 9999) -> debe fallar'
INSERT INTO fact_vuelo (sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino,
       sk_motivo_cancelacion, numero_vuelo, salida_programada, distancia_millas)
VALUES (20150105, 9, 9999, 1000, 1001, 0, 102, '09:00', 1235);

\echo '--- Prueba 2: vuelo cancelado sin motivo de cancelación -> debe fallar'
INSERT INTO fact_vuelo (sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino,
       sk_motivo_cancelacion, numero_vuelo, salida_programada, distancia_millas, es_cancelado)
VALUES (20150105, 10, 1000, 1000, 1001, 0, 103, '10:00', 1235, 1);

\echo '--- Prueba 3: el mismo vuelo cargado dos veces -> debe fallar'
INSERT INTO fact_vuelo (sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino,
       sk_motivo_cancelacion, numero_vuelo, salida_programada, retraso_salida_min, retraso_llegada_min,
       distancia_millas, es_puntual)
VALUES (20150105, 8, 1000, 1000, 1001, 0, 101, '08:15', 3, -2, 1235, 1);

\echo '--- Prueba 4: borrar un aeropuerto que tiene vuelos -> debe fallar'
DELETE FROM dim_aeropuerto WHERE sk_aeropuerto = 1000;

\echo '--- Prueba 5: distancia negativa -> debe fallar'
INSERT INTO fact_vuelo (sk_fecha, sk_hora_salida, sk_aerolinea, sk_aeropuerto_origen, sk_aeropuerto_destino,
       sk_motivo_cancelacion, numero_vuelo, salida_programada, distancia_millas)
VALUES (20150105, 11, 1000, 1000, 1001, 0, 105, '11:00', -50);

\echo '--- Control: la tabla de hechos conserva solo el vuelo válido de ejemplo'
SELECT numero_vuelo, salida_programada, retraso_llegada_min, es_puntual
FROM fact_vuelo
WHERE sk_aerolinea = 1000;

ROLLBACK;

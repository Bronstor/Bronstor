-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de vuelos en EE. UU. (2015)
-- Script 04: consultas analíticas de verificación
-- Cada consulta responde a un objetivo específico (OE) del proyecto.
-- =====================================================================

SET search_path TO dw_vuelos;

-- ---------------------------------------------------------------------
-- OE1. Puntualidad por aerolínea y mes
-- KPI: % de vuelos puntuales = vuelos con < 15 min de retraso / vuelos completados
-- ---------------------------------------------------------------------
SELECT a.nombre_aerolinea,
       f.mes,
       SUM(v.es_puntual + v.es_retrasado)                        AS vuelos_completados,
       ROUND(100.0 * SUM(v.es_puntual)
             / NULLIF(SUM(v.es_puntual + v.es_retrasado), 0), 1) AS pct_puntualidad
FROM fact_vuelo v
JOIN dim_aerolinea a ON a.sk_aerolinea = v.sk_aerolinea
JOIN dim_fecha     f ON f.sk_fecha     = v.sk_fecha
GROUP BY a.nombre_aerolinea, f.mes
ORDER BY a.nombre_aerolinea, f.mes;

-- ---------------------------------------------------------------------
-- OE2. Cancelaciones y desvíos por aerolínea, y cancelaciones por motivo
-- KPI: % de cancelación = vuelos cancelados / vuelos programados
-- ---------------------------------------------------------------------
SELECT a.nombre_aerolinea,
       COUNT(*)                                         AS vuelos_programados,
       SUM(v.es_cancelado)                              AS cancelados,
       ROUND(100.0 * SUM(v.es_cancelado) / COUNT(*), 2) AS pct_cancelacion,
       ROUND(100.0 * SUM(v.es_desviado)  / COUNT(*), 2) AS pct_desvio
FROM fact_vuelo v
JOIN dim_aerolinea a ON a.sk_aerolinea = v.sk_aerolinea
GROUP BY a.nombre_aerolinea
ORDER BY pct_cancelacion DESC;

SELECT m.descripcion                                       AS motivo,
       COUNT(*)                                            AS cancelados,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_del_total
FROM fact_vuelo v
JOIN dim_motivo_cancelacion m ON m.sk_motivo_cancelacion = v.sk_motivo_cancelacion
WHERE v.es_cancelado = 1
GROUP BY m.descripcion
ORDER BY cancelados DESC;

-- ---------------------------------------------------------------------
-- OE3. Causas de los retrasos
-- KPI: % de los minutos de retraso atribuidos a cada causa
-- ---------------------------------------------------------------------
SELECT c.causa,
       SUM(c.minutos)                                              AS minutos,
       ROUND(100.0 * SUM(c.minutos) / SUM(SUM(c.minutos)) OVER (), 1) AS pct_minutos
FROM fact_vuelo v
CROSS JOIN LATERAL (VALUES ('Aerolínea',      v.retraso_aerolinea_min),
                           ('Clima',          v.retraso_clima_min),
                           ('Sistema aéreo',  v.retraso_sistema_aereo_min),
                           ('Seguridad',      v.retraso_seguridad_min),
                           ('Avión tardío',   v.retraso_avion_tardio_min)) AS c(causa, minutos)
WHERE v.es_retrasado = 1
GROUP BY c.causa
ORDER BY minutos DESC;

-- ---------------------------------------------------------------------
-- OE4. Rutas con mayor retraso promedio de llegada
-- KPI: retraso promedio de llegada por ruta (origen-destino)
-- ---------------------------------------------------------------------
SELECT o.codigo_iata || '-' || d.codigo_iata   AS ruta,
       o.ciudad                                 AS ciudad_origen,
       d.ciudad                                 AS ciudad_destino,
       COUNT(*)                                 AS vuelos,
       ROUND(AVG(v.retraso_llegada_min), 1)     AS retraso_prom_llegada
FROM fact_vuelo v
JOIN dim_aeropuerto o ON o.sk_aeropuerto = v.sk_aeropuerto_origen
JOIN dim_aeropuerto d ON d.sk_aeropuerto = v.sk_aeropuerto_destino
WHERE v.retraso_llegada_min IS NOT NULL
GROUP BY o.codigo_iata, d.codigo_iata, o.ciudad, d.ciudad
HAVING COUNT(*) >= 100          -- mínimo de vuelos por ruta (ajustable)
ORDER BY retraso_prom_llegada DESC
LIMIT 20;

-- ---------------------------------------------------------------------
-- OE5. Retrasos según franja horaria y día de la semana
-- KPI: retraso promedio de salida y % de vuelos retrasados
-- ---------------------------------------------------------------------
SELECT h.franja_horaria,
       f.nombre_dia,
       ROUND(AVG(v.retraso_salida_min), 1)                       AS retraso_prom_salida,
       ROUND(100.0 * SUM(v.es_retrasado)
             / NULLIF(SUM(v.es_retrasado + v.es_puntual), 0), 1) AS pct_retrasados
FROM fact_vuelo v
JOIN dim_hora  h ON h.sk_hora  = v.sk_hora_salida
JOIN dim_fecha f ON f.sk_fecha = v.sk_fecha
GROUP BY h.franja_horaria, f.dia_semana, f.nombre_dia
ORDER BY MIN(h.sk_hora), f.dia_semana;

-- ---------------------------------------------------------------------
-- OE6. Eficiencia en tierra por aeropuerto de origen
-- KPI: tiempo promedio de rodaje antes del despegue (taxi-out)
-- ---------------------------------------------------------------------
SELECT o.region,
       o.codigo_iata,
       o.nombre_aeropuerto,
       COUNT(*)                            AS salidas,
       ROUND(AVG(v.taxi_salida_min), 1)    AS taxi_salida_prom
FROM fact_vuelo v
JOIN dim_aeropuerto o ON o.sk_aeropuerto = v.sk_aeropuerto_origen
WHERE v.taxi_salida_min IS NOT NULL
GROUP BY o.region, o.codigo_iata, o.nombre_aeropuerto
ORDER BY taxi_salida_prom DESC;

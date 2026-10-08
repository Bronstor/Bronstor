-- =====================================================================
-- Proyecto Base de Datos 3 - Data Warehouse de Fórmula 1
-- Script 04: consultas analíticas de verificación
-- Cada consulta responde a un objetivo específico (OE) del proyecto y
-- demuestra que el modelo dimensional contiene los datos necesarios.
-- =====================================================================

SET search_path TO dw_f1;

-- ---------------------------------------------------------------------
-- OE1. Conversión de la posición de salida en resultado final
-- KPI: % de victorias desde la pole y promedio de posiciones ganadas
-- ---------------------------------------------------------------------
SELECT c.temporada,
       SUM(f.es_pole)                                   AS largadas_desde_pole,
       SUM(f.es_victoria * f.es_pole)                   AS victorias_desde_pole,
       ROUND(100.0 * SUM(f.es_victoria * f.es_pole)
             / NULLIF(SUM(f.es_pole), 0), 1)            AS pct_conversion_pole,
       ROUND(AVG(f.posiciones_ganadas), 2)              AS prom_posiciones_ganadas
FROM fact_resultado_carrera f
JOIN dim_carrera c ON c.sk_carrera = f.sk_carrera
GROUP BY c.temporada
ORDER BY c.temporada;

-- ---------------------------------------------------------------------
-- OE2. Dominio de las escuderías por temporada
-- KPI: % de victorias, % de podios y cuota de puntos de la temporada
-- ---------------------------------------------------------------------
WITH por_escuderia AS (
    SELECT c.temporada,
           e.nombre_escuderia,
           SUM(f.es_victoria) AS victorias,
           SUM(f.es_podio)    AS podios,
           SUM(f.puntos)      AS puntos
    FROM fact_resultado_carrera f
    JOIN dim_carrera   c ON c.sk_carrera   = f.sk_carrera
    JOIN dim_escuderia e ON e.sk_escuderia = f.sk_escuderia
    GROUP BY c.temporada, e.nombre_escuderia
)
SELECT temporada,
       nombre_escuderia,
       victorias,
       podios,
       puntos,
       ROUND(100.0 * victorias / NULLIF(SUM(victorias) OVER (PARTITION BY temporada), 0), 1) AS pct_victorias,
       ROUND(100.0 * podios    / NULLIF(SUM(podios)    OVER (PARTITION BY temporada), 0), 1) AS pct_podios,
       ROUND(100.0 * puntos    / NULLIF(SUM(puntos)    OVER (PARTITION BY temporada), 0), 1) AS cuota_puntos
FROM por_escuderia
ORDER BY temporada, puntos DESC;

-- OE2 (variante). Victorias por escudería y década (jerarquía de la dimensión tiempo)
SELECT t.nombre_decada,
       e.nombre_escuderia,
       SUM(f.es_victoria) AS victorias
FROM fact_resultado_carrera f
JOIN dim_tiempo    t ON t.sk_tiempo    = f.sk_tiempo
JOIN dim_escuderia e ON e.sk_escuderia = f.sk_escuderia
GROUP BY t.decada, t.nombre_decada, e.nombre_escuderia
HAVING SUM(f.es_victoria) > 0
ORDER BY t.decada, victorias DESC;

-- ---------------------------------------------------------------------
-- OE3. Confiabilidad de las escuderías
-- KPI: tasa de abandono, tasa de finalización y causas de abandono
-- ---------------------------------------------------------------------
SELECT c.temporada,
       e.nombre_escuderia,
       COUNT(*)                                          AS participaciones,
       SUM(f.es_abandono)                                AS abandonos,
       ROUND(100.0 * SUM(f.es_abandono)   / COUNT(*), 1) AS tasa_abandono,
       ROUND(100.0 * SUM(f.es_finalizado) / COUNT(*), 1) AS tasa_finalizacion
FROM fact_resultado_carrera f
JOIN dim_carrera   c ON c.sk_carrera   = f.sk_carrera
JOIN dim_escuderia e ON e.sk_escuderia = f.sk_escuderia
GROUP BY c.temporada, e.nombre_escuderia
ORDER BY c.temporada, tasa_abandono DESC;

SELECT s.categoria_estado,
       COUNT(*)                                            AS abandonos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_del_total
FROM fact_resultado_carrera f
JOIN dim_estado s ON s.sk_estado = f.sk_estado
WHERE f.es_abandono = 1
GROUP BY s.categoria_estado
ORDER BY abandonos DESC;

-- ---------------------------------------------------------------------
-- OE4. Rendimiento histórico de los pilotos
-- KPI: puntos por carrera normalizados, tasa de victorias y de podios,
--      edad promedio al ganar
-- ---------------------------------------------------------------------
SELECT p.nombre_completo,
       COUNT(*)                                                   AS participaciones,
       SUM(f.es_victoria)                                         AS victorias,
       SUM(f.es_podio)                                            AS podios,
       ROUND(SUM(f.puntos_sistema_actual) / COUNT(*), 2)          AS puntos_norm_por_carrera,
       ROUND(100.0 * SUM(f.es_victoria) / COUNT(*), 1)            AS tasa_victorias,
       ROUND(100.0 * SUM(f.es_podio)    / COUNT(*), 1)            AS tasa_podios,
       ROUND(AVG(f.edad_piloto) FILTER (WHERE f.es_victoria = 1), 1) AS edad_prom_al_ganar
FROM fact_resultado_carrera f
JOIN dim_piloto p ON p.sk_piloto = f.sk_piloto
GROUP BY p.sk_piloto, p.nombre_completo
HAVING COUNT(*) >= 20          -- mínimo de participaciones para comparar (ajustable)
ORDER BY puntos_norm_por_carrera DESC
LIMIT 20;

-- OE4 (métrica semiaditiva). Campeón de cada temporada: se toma el valor
-- de puntos_acumulados_temporada en la última ronda; no se suma entre rondas.
SELECT DISTINCT ON (c.temporada)
       c.temporada,
       p.nombre_completo               AS campeon,
       f.puntos_acumulados_temporada   AS puntos_finales
FROM fact_resultado_carrera f
JOIN dim_carrera c ON c.sk_carrera = f.sk_carrera
JOIN dim_piloto  p ON p.sk_piloto  = f.sk_piloto
WHERE f.posicion_campeonato = 1
ORDER BY c.temporada, c.ronda DESC;

-- ---------------------------------------------------------------------
-- OE5. Caracterización de circuitos y países sede
-- KPI: Grandes Premios disputados, índice de adelantamiento,
--      tasa de abandono y % de victorias desde la pole
-- ---------------------------------------------------------------------
SELECT ci.continente,
       ci.pais,
       ci.nombre_circuito,
       COUNT(DISTINCT f.sk_carrera)                          AS grandes_premios,
       ROUND(AVG(f.posiciones_ganadas), 2)                   AS indice_adelantamiento,
       ROUND(100.0 * SUM(f.es_abandono) / COUNT(*), 1)       AS tasa_abandono,
       ROUND(100.0 * SUM(f.es_victoria * f.es_pole)
             / NULLIF(SUM(f.es_pole), 0), 1)                 AS pct_victorias_desde_pole
FROM fact_resultado_carrera f
JOIN dim_circuito ci ON ci.sk_circuito = f.sk_circuito
GROUP BY ci.continente, ci.pais, ci.nombre_circuito
ORDER BY grandes_premios DESC;

-- ---------------------------------------------------------------------
-- OE6. Evolución del ritmo por circuito (datos desde 2004)
-- KPI: mejor vuelta, velocidad media de vuelta rápida y variación anual
-- ---------------------------------------------------------------------
WITH ritmo AS (
    SELECT ci.nombre_circuito,
           c.temporada,
           MIN(f.tiempo_vuelta_rapida_ms)           AS mejor_vuelta_ms,
           ROUND(AVG(f.velocidad_vuelta_rapida_kmh), 3) AS velocidad_media_kmh
    FROM fact_resultado_carrera f
    JOIN dim_carrera  c  ON c.sk_carrera   = f.sk_carrera
    JOIN dim_circuito ci ON ci.sk_circuito = f.sk_circuito
    WHERE f.tiempo_vuelta_rapida_ms IS NOT NULL
    GROUP BY ci.nombre_circuito, c.temporada
)
SELECT nombre_circuito,
       temporada,
       TO_CHAR(make_interval(secs => mejor_vuelta_ms / 1000.0), 'MI:SS.MS') AS mejor_vuelta,
       velocidad_media_kmh,
       ROUND(100.0 * (velocidad_media_kmh - LAG(velocidad_media_kmh) OVER w)
             / LAG(velocidad_media_kmh) OVER w, 2)                          AS variacion_pct
FROM ritmo
WINDOW w AS (PARTITION BY nombre_circuito ORDER BY temporada)
ORDER BY nombre_circuito, temporada;

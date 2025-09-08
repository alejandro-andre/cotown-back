-- Stabilised
WITH months AS (
  SELECT generate_series(1, 12) AS month_num
)
SELECT
  r."Code",
  m.month_num AS "Date_price",
  COALESCE(rs."Occupancy", 0) / 100 AS "Occupancy",
  COALESCE(rs."Pct_long", 0)/ 100 AS "Pct_long",
  COALESCE(rs."Pct_medium", 0)/ 100 AS "Pct_medium",
  COALESCE(rs."Pct_short", 0)/ 100 AS "Pct_short",
  COALESCE(rs."Leakage", 0)/ 100 AS "Leakage"
FROM "Resource"."Resource" r
  CROSS JOIN months m
  LEFT JOIN "Resource"."Resource_stabilised" rs ON rs."Resource_id" = r.id AND rs."Date_price" = m.month_num
WHERE r."Resource_type" = 'piso'
ORDER BY 1, 2
;
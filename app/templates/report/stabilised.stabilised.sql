-- Stabilised
WITH months AS (
  SELECT generate_series(1, 12) AS month_num
)
SELECT
  r."Code",
  m.month_num AS "Date_price",
  rs."Occupancy"/100 AS "Occupancy",
  rs."Rent_short"/100 AS "Rent_short",
  rs."Rent_medium"/100 AS "Rent_medium",
  rs."Rent_long"/100 AS "Rent_long"
FROM "Resource"."Resource" r
  CROSS JOIN months m
  LEFT JOIN "Resource"."Resource_stabilised" rs ON rs."Resource_id" = r.id AND rs."Date_price" = m.month_num
WHERE r."Resource_type" = 'piso'
ORDER BY 1, 2
;
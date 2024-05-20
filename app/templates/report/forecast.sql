WITH
"Extras" AS (
  -- Extras
  SELECT r.id,
    EXP(SUM(LN(1 + COALESCE(rat."Increment", 0) / 100))) AS "Extra"
  FROM "Resource"."Resource" r
    LEFT JOIN "Resource"."Resource_amenity" ra ON ra."Resource_id" = r.id 
    LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
  GROUP BY 1
),
"Prices" AS (
  -- Meses del año
  WITH
  "Dates" AS (
    SELECT 
      date_trunc('month', generate_series)::date AS "Date",
      CASE 
        WHEN EXTRACT(MONTH FROM generate_series) < 9 THEN
          EXTRACT(YEAR FROM generate_series) 
        ELSE
          1 + EXTRACT(YEAR FROM generate_series) 
      END AS "Year"
    FROM 
      generate_series('2024-01-01'::date, '2024-12-31'::date, '1 month'::interval)
  )
  -- Precios por año
  SELECT d."Date", r.id, r."Flat_id",
    pd."Rent_short" * pr."Multiplier" AS "Rent_short",
    pd."Rent_medium" * pr."Multiplier" AS "Rent_medium",
    pd."Rent_long" * pr."Multiplier" AS "Rent_long"
  FROM "Resource"."Resource" r
    INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" 
      AND pd."Flat_type_id" = r."Flat_type_id"
      AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
    INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
    CROSS JOIN "Dates" d
  WHERE r."Resource_type" <> 'piso'
    AND pd."Year" = d."Year"
)
SELECT
  p."Date",
  r."Code",
  ROUND(AVG(p."Rent_short" * e."Extra"), 2) AS "Short",
  ROUND(AVG(p."Rent_medium" * e."Extra"), 2) AS "Medium",
  ROUND(AVG(p."Rent_long" * e."Extra"), 2) AS "Long"
FROM "Prices" p
  LEFT JOIN "Extras" e ON p.id = e.id
  LEFT JOIN "Resource"."Resource" r ON r.id = p."Flat_id"
GROUP BY 1, 2
ORDER BY 2, 1;
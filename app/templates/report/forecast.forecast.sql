WITH
"Extras" AS (
  -- Extras, por plaza
  SELECT r.id,
    EXP(SUM(LN(1 + COALESCE(rat."Increment", 0) / 100))) AS "Extra"
  FROM "Resource"."Resource" r
    LEFT JOIN "Resource"."Resource_amenity" ra ON ra."Resource_id" = r.id 
    LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
  GROUP BY 1
),
"Details" AS (
  WITH
  "Dates" AS (
    -- Meses del año, meses consolidados y cambio de curso
    SELECT 
      date_trunc('month', generate_series)::date AS "Date",
      CASE
        WHEN EXTRACT(MONTH FROM generate_series) BETWEEN 3 AND 8 THEN
          (EXTRACT(YEAR FROM generate_series) || '-02-01')::date
        WHEN EXTRACT(MONTH FROM generate_series) BETWEEN 11 AND 12 THEN
          (EXTRACT(YEAR FROM generate_series) || '-10-01')::date
        ELSE
          date_trunc('month', generate_series)::date
      END AS "Consolidated_date",
      CASE 
        WHEN EXTRACT(MONTH FROM generate_series) < 9 THEN
          EXTRACT(YEAR FROM generate_series) 
        ELSE
          1 + EXTRACT(YEAR FROM generate_series) 
      END AS "Year"
    FROM 
      generate_series(%(fdesde)s::date, %(fhasta)s::date - '1 day'::interval, '1 month'::interval)
  )
  -- Detalles por plaza
  SELECT 
    r.id, 
    d."Date", 
    substring(r."Code", 1, 6) AS "Building",
    CASE
      WHEN EXISTS (SELECT ra.id FROM "Resource"."Resource_availability" ra WHERE ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Date" AND ra."Date_to" >= d."Date") THEN 0
      ELSE 1
    END AS "Beds",
    CASE
      WHEN EXISTS (SELECT ra.id FROM "Resource"."Resource_availability" ra WHERE ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Consolidated_date" AND ra."Date_to" >= d."Consolidated_date") THEN 0
      ELSE 1
    END AS "Consolidated_beds",
    pd."Rent_short" * pr."Multiplier" AS "Rent_short",
    pd."Rent_medium" * pr."Multiplier" AS "Rent_medium",
    pd."Rent_long" * pr."Multiplier" AS "Rent_long",
    r."Management_fee"
  FROM "Resource"."Resource" r
    INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" 
      AND pd."Flat_type_id" = r."Flat_type_id"
      AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
    INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
    INNER JOIN "Building"."Building" b ON b."id" = r."Building_id" 
    CROSS JOIN "Dates" d
  WHERE b."Active"
    AND pd."Year" = d."Year"
    AND (r."Place_type_id" < 300 OR r."Flat_type_id" = 4)
)
SELECT
  p."Date",
  p."Building",
  SUM(p."Beds") AS "Beds",
  SUM(p."Consolidated_beds") + (SUM(p."Beds") - SUM(p."Consolidated_beds")) / 2.0 AS "Consolidated_beds",
  ROUND(AVG(p."Rent_short" * e."Extra"), 2) AS "Short",
  ROUND(AVG(p."Rent_medium" * e."Extra"), 2) AS "Medium",
  ROUND(AVG(p."Rent_long" * e."Extra"), 2) AS "Long",
  AVG(p."Management_fee") / 100.0 AS "Management_fee"
FROM "Details" p
LEFT JOIN "Extras" e ON p.id = e.id
GROUP BY 1, 2
ORDER BY 2, 1;
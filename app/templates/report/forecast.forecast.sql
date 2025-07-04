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
    substring(r."Code", 1, 12) AS "Resource",
    CASE
      WHEN EXISTS (
        SELECT ra.id 
        FROM "Resource"."Resource_availability" ra 
        INNER JOIN "Resource"."Resource_status" rs on rs.id = ra."Status_id"
        WHERE NOT rs."Available" AND ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Date" AND ra."Date_to" >= d."Date"
      ) THEN 0
      ELSE 1
    END AS "Beds",
    CASE
      WHEN EXISTS (
        SELECT ra.id 
        FROM "Resource"."Resource_availability" ra 
        INNER JOIN "Resource"."Resource_status" rs on rs.id = ra."Status_id"
        WHERE NOT rs."Available" AND ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Consolidated_date" AND ra."Date_to" >= d."Consolidated_date"
      ) THEN 0
      ELSE 1
    END AS "Consolidated_beds",
    pd."Rent_short" * pr."Multiplier" AS "Rent_short",
    pd."Rent_medium" * pr."Multiplier" AS "Rent_medium",
    pd."Rent_long" * pr."Multiplier" AS "Rent_long",
    r."Management_fee"
  FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b."id" = r."Building_id" 
    LEFT JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" 
      AND pd."Flat_type_id" = r."Flat_type_id"
      AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
    LEFT JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
    LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    CROSS JOIN "Dates" d
  WHERE (pd."Year" = d."Year" OR pd."Year" IS NULL)
    AND (COALESCE(rpt."Code", '') NOT LIKE 'DUI%%' OR rft."Code" = 'APT1')
)
SELECT
  p."Date",
  p."Resource",
  SUM(p."Beds") AS "Beds",
  SUM(p."Consolidated_beds") + (SUM(p."Beds") - SUM(p."Consolidated_beds")) / 2.0 AS "Consolidated_beds",
  AVG(p."Rent_short" * e."Extra") AS "Short",
  AVG(p."Rent_medium" * e."Extra") AS "Medium",
  AVG(p."Rent_long" * e."Extra") AS "Long",
  AVG(p."Management_fee") / 100.0 AS "Management_fee"
FROM "Details" p
LEFT JOIN "Extras" e ON p.id = e.id
GROUP BY 1, 2
ORDER BY 2, 1;
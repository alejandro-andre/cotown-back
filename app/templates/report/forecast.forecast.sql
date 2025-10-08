WITH 
-- Extras, por plaza
"Extras" AS (
  SELECT r.id,
    1 AS "Extra"-- EXP(SUM(LN(1 + COALESCE(rat."Increment", 0) / 100))) AS "Extra"
  FROM "Resource"."Resource" r
    LEFT JOIN "Resource"."Resource_amenity" ra ON ra."Resource_id" = r.id 
    LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
  GROUP BY 1
),
-- Meses del año y cambio de curso
"Dates" AS (
  SELECT 
    date_trunc('month', generate_series)::date AS "Date",
    CASE 
  	WHEN EXTRACT(MONTH FROM generate_series) < 9 THEN EXTRACT(YEAR FROM generate_series) 
      ELSE 1 + EXTRACT(YEAR FROM generate_series) 
    END AS "Year"
  FROM 
    generate_series(%(fdesde)s::date, %(fhasta)s::date - '1 day'::interval, '1 month'::interval)
),
-- Precios por plaza
"Prices" AS (
  SELECT
  	substring(r."Code", 1, 12) AS "Code",
    d."Date", 
  	r."Flat_id",
  	rft."Code" AS "Flat_type",
  	rpt."Code" AS "Place_type",
    pd."Rent_short" * pr."Multiplier" * e."Extra" AS "Rent_short",
    pd."Rent_medium" * pr."Multiplier" * e."Extra" AS "Rent_medium",
    pd."Rent_long" * pr."Multiplier" * e."Extra" AS "Rent_long",
    pd."Rent_group" * pr."Multiplier" * e."Extra" AS "Rent_group",
    CASE
      WHEN EXISTS (
        SELECT ra.id 
        FROM "Resource"."Resource_availability" ra 
        INNER JOIN "Resource"."Resource_status" rs on rs.id = ra."Status_id"
        WHERE NOT rs."Available" AND ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Date" AND ra."Date_to" >= d."Date"
      ) THEN 0
      ELSE 1
    END AS "Beds"
  FROM "Resource"."Resource" r
    CROSS JOIN "Dates" d
    LEFT JOIN "Extras" e ON r.id = e.id
    LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    LEFT JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
    LEFT JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
  WHERE (pd."Year" = d."Year" OR pd."Year" IS NULL)
    AND (
      r."Resource_type" = 'plaza'
      OR (r."Resource_type" = 'habitacion' AND rpt."Code" NOT LIKE 'DUI%%')
      OR (r."Resource_type" = 'piso' AND rft."Code" = 'APT1')
    )
    AND NOT EXISTS (
      SELECT 1
      FROM "Booking"."Booking_detail" bd
        INNER JOIN "Resource"."Resource_availability" ra ON ra.id = bd."Availability_id"
        INNER JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
      WHERE bd."Resource_id" = r.id 
        AND bd."Date_from" <= d."Date" 
        AND bd."Date_to" >= d."Date"
        AND NOT rs."Available"
    )
  ORDER BY 1, 2
),
-- Media de precios
"Averages" AS (
  SELECT
  	p."Code",
    p."Date" AS "Date_price",
  	p."Flat_id",
    SUM(p."Beds") AS "Beds",
    ROUND(AVG(p."Rent_short"), 2) AS "Short",
    ROUND(AVG(p."Rent_medium"), 2) AS "Medium",
    ROUND(AVG(p."Rent_long"), 2) AS "Long",
    ROUND(AVG(p."Rent_group"), 2) AS "Group"
  FROM "Prices" p
  GROUP BY 1, 2, 3
),
-- Plazas
"Flats" AS (
  SELECT
  	r.id,
  	r."Code",
    r."Management_fee" / 100.0 AS "Management_fee",
    d."Date" AS "Date_price"
  FROM "Resource"."Resource" r
    CROSS JOIN "Dates" d
    LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
  WHERE r."Resource_type" = 'piso'
  ORDER BY 1, 2
)
SELECT 
  f."Code", 
  f."Date_price", 
  COALESCE(rf."Beds", 0) AS "Beds",
  COALESCE(rf."Occupancy", 0) / 100 AS "Occupancy",
  COALESCE(rf."Rent_long", 0) AS "Rent_long",
  COALESCE(rf."Rent_medium", 0) AS "Rent_medium",
  COALESCE(rf."Rent_short", 0) AS "Rent_short",
  COALESCE(rf."Rent_group", 0) AS "Rent_group",
  COALESCE(rf."Pct_long", 0) / 100 AS "Pct_long",
  COALESCE(rf."Pct_medium", 0) / 100 AS "Pct_medium",
  COALESCE(rf."Pct_short", 0) / 100 AS "Pct_short",
  COALESCE(rf."Discount", 0) / 100 AS "Discount",
  COALESCE(rf."Services", 0) AS "Services",
  COALESCE(rf."Final_cleaning", 0) AS "Final_cleaning",
  COALESCE(rf."Booking_fee", 0) AS "Booking_fee",
  COALESCE(rf."Reinvoices", 0) AS "Reinvoices",
  COALESCE(a."Beds", 0) AS "Available_beds",
  f."Management_fee",
  a."Long",
  a."Medium",
  a."Short",
  a."Group"
FROM "Flats" f
  LEFT JOIN "Averages" a ON a."Flat_id" = f.id AND a."Date_price" = f."Date_price"
  LEFT JOIN "Resource"."Resource_forecast" rf ON rf."Resource_id" = f.id AND rf."Date_price" = f."Date_price"
ORDER BY 1, 2
;
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
    -- Meses del año y cambio de curso
    SELECT 
      date_trunc('month', generate_series)::date AS "Date",
      CASE 
    	WHEN EXTRACT(MONTH FROM generate_series) < 9 THEN EXTRACT(YEAR FROM generate_series) 
        ELSE 1 + EXTRACT(YEAR FROM generate_series) 
      END AS "Year"
    FROM 
      generate_series(%(fdesde)s::date, %(fhasta)s::date - '1 day'::interval, '1 month'::interval)
  )
  -- Detalles por plaza
  SELECT
    r."Code",
    r."Resource_type",
    rft."Code",
    rpt."Code",
    substring(r."Code", 1, 12) AS "Resource",
    r.id,
    CASE
      WHEN r."Resource_type" = 'piso'THEN r.id
      ELSE r."Flat_id"
    END AS "Flat_id",
    d."Date", 
    CASE
      WHEN EXISTS (
        SELECT ra.id 
        FROM "Resource"."Resource_availability" ra 
        INNER JOIN "Resource"."Resource_status" rs on rs.id = ra."Status_id"
        WHERE NOT rs."Available" AND ra."Resource_id" = r."Flat_id" AND ra."Date_from" <= d."Date" AND ra."Date_to" >= d."Date"
      ) THEN 0
      ELSE 1
    END AS "Beds",
    pr."Multiplier",
    pd."Rent_short" * pr."Multiplier" AS "Rent_short",
    pd."Rent_medium" * pr."Multiplier" AS "Rent_medium",
    pd."Rent_long" * pr."Multiplier" AS "Rent_long",
    pd."Rent_group" * pr."Multiplier" AS "Rent_group",
    r."Management_fee"
  FROM "Resource"."Resource" r
    CROSS JOIN "Dates" d
    INNER JOIN "Building"."Building" b ON b."id" = r."Building_id" 
    LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    LEFT JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" 
      AND pd."Flat_type_id" = r."Flat_type_id"
      AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
    LEFT JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
  WHERE (pd."Year" = d."Year" OR pd."Year" IS NULL)
    AND (
      r."Resource_type" = 'plaza'
      OR (r."Resource_type" = 'habitacion' AND rpt."Code" NOT LIKE 'DUI%%')
      OR (r."Resource_type" = 'piso' AND rft."Code" = 'APT1')
    )
  ORDER BY 1
)
SELECT
  p."Date" AS "Date_price",
  p."Resource" AS "Code",
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
  SUM(p."Beds") AS "Beds",
  ROUND(AVG(p."Rent_short" * e."Extra"), 2) AS "Short",
  ROUND(AVG(p."Rent_medium" * e."Extra"), 2) AS "Medium",
  ROUND(AVG(p."Rent_long" * e."Extra"), 2) AS "Long",
  ROUND(AVG(p."Rent_group"), 2) AS "Group",
  MAX(p."Management_fee") / 100.0 AS "Management_fee"
FROM "Details" p
  LEFT JOIN "Extras" e ON p.id = e.id
  LEFT JOIN "Resource"."Resource_forecast" rf ON rf."Resource_id" = p."Flat_id" AND rf."Date_price" = p."Date"
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
ORDER BY 2, 1;
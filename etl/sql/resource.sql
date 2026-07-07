SELECT 
  r."Code" AS "id",
  r."Resource_type"::text AS "type",
  p."Document" AS "owner", 
  l."Name_en" AS "location", 
  COALESCE(rs."Name", s."Name") AS "segment",
  SUBSTRING(r."Code", 1, 6) AS "building",
  SUBSTRING(r."Code", 1, 12) AS "flat",
  CASE
    WHEN r."Resource_type" = 'local' THEN 'RETAIL'
    WHEN r."Resource_type" = 'parking' THEN 'PARKING'
    WHEN r."Resource_type" = 'trastero' THEN 'STORAGE'
    ELSE rft."Code"
  END AS "flat_type",
  CASE
    WHEN r."Resource_type" = 'local' THEN 'RETAIL'
    WHEN r."Resource_type" = 'parking' THEN 'PARKING'
    WHEN r."Resource_type" = 'trastero' THEN 'STORAGE'
    WHEN rpt."Code" IS NULL THEN 'FLAT'
    ELSE rpt."Code" 
  END AS "place_type",
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "billing_type",
  b."Estabilised_date" AS "estabilised_date",
  COALESCE(r."Area", 0) AS "area",
  COALESCE(r."Area_woc", 0) AS "area_woc",
  CASE 
  	WHEN r."Resource_type" = 'plaza' THEN 1
  	WHEN r."Resource_type" = 'habitacion' THEN (
  		SELECT GREATEST(1, COUNT(*))
  		FROM "Resource"."Resource" rr
  		WHERE rr."Room_id" = r.id
  	)
  	ELSE (
  		SELECT COUNT("Flat_id") - COUNT("Room_id") / 2
  		FROM "Resource"."Resource" rr
  		WHERE rr."Flat_id" = r.id
  	)
  END AS "beds",
  CASE
  	WHEN r."Resource_type" = 'plaza' THEN 0
  	WHEN r."Resource_type" = 'piso' THEN (
  		SELECT COUNT(*)
  		FROM "Resource"."Resource" rr
  		WHERE rr."Flat_id" = r.id
  		AND rr."Resource_type" = 'habitacion'
  	)
  	ELSE 1
  END AS "rooms",
  r."Renovation_date" AS "renovation_date",
  r."Energy_certificate" AS "energy_certificate",
  r."Energy_certificate_rate" AS "energy_certificate_rate",
  r."Last_LAU_date" AS "last_lau_date",
  r."Last_LAU_free_date" AS "last_lau_free_date",
  r."Last_LAU_rent" AS "last_lau_rent",
  r."Max_LAU_rent" AS "max_lau_rent",
  r."Index_rent" AS "index_rent",
  COALESCE(NULLIF(r."Limit_type"::text, ''), 'libre') AS "limit_type",
  r."Max_rent" AS "max_rent",
  r."Max_services" AS "max_services",
  r."Max_expenses" AS "max_expenses",
  r."Max_furniture" AS "max_furniture",
  r."Big_renovation_date" AS "big_renovation_date",
  r."Occupancy_certificate" AS "occupancy_certificate",
  r."Max_utility" AS "max_utility",
  r."HOA" AS "hoa",
  r."LAU_applicable" AS "lau_applicable"
FROM "Resource"."Resource" r
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
INNER JOIN "Auxiliar"."Segment" s on s.id = b."Segment_id"
INNER JOIN "Geo"."District" d ON d.id = b."District_id"
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
LEFT JOIN "Auxiliar"."Segment" rs ON rs.id = r."Segment_id"

UNION

SELECT DISTINCT
  SUBSTRING(r."Code", 1, 6) AS "id",
  'building' AS "type",
  p."Document" AS "owner",
  l."Name_en" AS "location",
  s."Name" AS "segment",
  SUBSTRING(r."Code", 1, 6) AS "building",
  SUBSTRING(r."Code", 1, 6) AS "flat",
  NULL AS "flat_type",
  NULL AS "place_type",
  '' AS "billing_type",
  b."Estabilised_date" AS "estabilised_date",
  0 AS "area",
  0 AS "area_woc",
  0 AS "beds",
  0 AS "rooms",
  NULL::date AS "renovation_date",
  NULL::varchar AS "energy_certificate",
  NULL::varchar AS "energy_certificate_rate",
  NULL::date AS "last_lau_date",
  NULL::date AS "last_lau_free_date",
  NULL::numeric AS "last_lau_rent",
  NULL::numeric AS "max_lau_rent",
  NULL::numeric AS "index_rent",
  'libre'::varchar AS "limit_type",
  NULL::numeric AS "max_rent",
  NULL::numeric AS "max_services",
  NULL::numeric AS "max_expenses",
  NULL::numeric AS "max_furniture",
  NULL::date AS "big_renovation_date",
  NULL::varchar AS "occupancy_certificate",
  NULL::numeric AS "max_utility",
  NULL::boolean AS "hoa",
  NULL::boolean AS "lau_applicable"
FROM "Resource"."Resource" r
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
INNER JOIN "Auxiliar"."Segment" s on s.id = b."Segment_id"
INNER JOIN "Geo"."District" d ON d.id = b."District_id"
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"

ORDER BY 1
;
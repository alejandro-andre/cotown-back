SELECT 
  r."Code" AS "id",
  r."Resource_type"::text AS "type",
  p."Document" AS "owner", 
  l."Name_en" AS "location", 
  b."Start_date" AS "start_date",
  s."Name" AS "segment",
  SUBSTRING(r."Code", 1, 6) AS "building", 
  b."Name" as "building_name",
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
  b."Estabilised_date"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
INNER JOIN "Auxiliar"."Segment" s on s.id = b."Segment_id"
INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
WHERE r."Resource_type" IN ('piso', 'habitacion', 'plaza', 'local', 'parking', 'trastero')

UNION

SELECT DISTINCT
  SUBSTRING(r."Code", 1, 6) AS "id",
  'edificio' AS "type",
  p."Document" AS "owner", 
  l."Name_en" AS "location", 
  b."Start_date" AS "start_date",
  s."Name" AS "segment",
  SUBSTRING(r."Code", 1, 6) AS "building", 
  b."Name" as "building_name",
  SUBSTRING(r."Code", 1, 6) AS "flat",
  NULL AS "flat_type",
  NULL AS "place_type",
  '' AS "billing_type",
  b."Estabilised_date"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
INNER JOIN "Auxiliar"."Segment" s on s.id = b."Segment_id"
INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
WHERE r."Resource_type" IN ('piso', 'habitacion', 'plaza', 'local', 'parking', 'trastero')
;
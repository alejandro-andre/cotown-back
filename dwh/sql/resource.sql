SELECT 
  r."Code" AS "id",
  p."Document" AS "owner", 
  l."Name" AS "location", 
  SUBSTRING(r."Code", 1, 6) AS "building", 
  SUBSTRING(r."Code", 1, 12) AS "flat",
  rft."Code" AS "flat_type",
  rpt."Code" AS "place_type"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 

UNION

SELECT DISTINCT
  SUBSTRING(r."Code", 1, 6) AS "id",
  p."Document" AS "owner", 
  l."Name" AS "location", 
  SUBSTRING(r."Code", 1, 6) AS "building", 
  NULL AS "flat",
  NULL AS "flat_type",
  NULL AS "place_type"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
;
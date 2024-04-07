SELECT 
  r."Code" AS "id",
  p."Document" AS "owner", 
  l."Name" AS "location", 
  substring(r."Code", 1, 6) AS "building", 
  substring(r."Code", 1, 12) AS "flat"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
INNER JOIN "Geo"."Location" l ON l.id = d."Location_id";
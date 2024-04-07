SELECT 
  r."Code" AS "id",
  p."Document" AS "owner_id", 
  substring(r."Code", 1, 6) AS "building", 
  substring(r."Code", 1, 12) AS "flat"
FROM "Resource"."Resource" r 
INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id";
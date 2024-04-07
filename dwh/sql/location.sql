SELECT 
  l."Name" AS "id",
  p."Name" AS "province",
  c."Name" AS "country"
FROM "Geo"."Location" l 
INNER JOIN "Geo"."Province" p ON p.id = l."Province_id" 
INNER JOIN "Geo"."Country" c ON c.id = p."Country_id";
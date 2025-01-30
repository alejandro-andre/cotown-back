SELECT DISTINCT 
  p."Document" AS "id", 
  CASE WHEN p."Document" = 'A88445762' THEN 'Vandor' ELSE 'Third party' END AS "type",  
  CASE WHEN p."Document" = 'A88445762' THEN 1 ELSE 2 END AS "order",  
  p."Name" AS "name" 
FROM "Provider"."Provider" p
  INNER JOIN "Resource"."Resource" r ON r."Owner_id" = p.id;
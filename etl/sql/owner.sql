SELECT 
  p."Document" AS "id", 
  CASE WHEN p."Document" = 'A88445762' THEN 'Vandor' ELSE 'Terceros' END AS "type",  
  p."Name" AS "name" 
FROM "Provider"."Provider" p;
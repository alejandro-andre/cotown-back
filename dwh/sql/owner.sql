SELECT 
  p."Document" AS "id", 
  CASE 
  	WHEN p.id = 10 THEN 'Vandor'
  	ELSE 'Terceros'
  END AS "type",  
  p."Name" AS "name" 
FROM "Provider"."Provider" p;
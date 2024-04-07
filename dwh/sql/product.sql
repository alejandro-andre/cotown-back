SELECT p."Name" AS "id", pt."Name" AS "type"
FROM "Billing"."Product" p
INNER JOIN "Billing"."Product_type" pt ON pt.id = p."Product_type_id" 
WHERE pt.id <> 2;
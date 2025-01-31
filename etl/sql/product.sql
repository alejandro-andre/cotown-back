SELECT p."Name_en" AS "id", pt."Name_en" AS "type"
FROM "Billing"."Product" p
INNER JOIN "Billing"."Product_type" pt ON pt.id = p."Product_type_id";
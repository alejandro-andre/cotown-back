SELECT 
  'FLAT' AS "id",
  'Flat' AS "group",
  1 AS "order",
  'Private apartment' AS "name"
UNION
SELECT 
  "Code" AS "id",
  CASE 
	  WHEN SUBSTRING("Code", 1, 1) = 'I' THEN 'Single'
	  WHEN SUBSTRING("Code", 1, 3) = 'DUI' THEN 'DSU'
	  ELSE 'Double'
  END AS "group",
  CASE 
	  WHEN SUBSTRING("Code", 1, 1) = 'I' THEN 2
	  WHEN SUBSTRING("Code", 1, 3) = 'DUI' THEN 4
	  ELSE 3
  END AS "order",
  "Name_en" AS "name"
FROM "Resource"."Resource_place_type"
ORDER BY 1
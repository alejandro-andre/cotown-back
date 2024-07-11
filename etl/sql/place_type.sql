SELECT 
  "Code" AS "id",
  CASE 
	  WHEN SUBSTRING("Code", 1, 1) = 'I' THEN 'Single'
	  WHEN SUBSTRING("Code", 1, 3) = 'DUI' THEN 'DSU'
	  ELSE 'Double'
  END AS "group",
  "Name_en" AS "name"
FROM "Resource"."Resource_place_type"
ORDER BY 1
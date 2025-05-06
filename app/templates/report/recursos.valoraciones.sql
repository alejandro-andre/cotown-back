SELECT 
  r."Code" AS "Resource.Code", 
  rv."Valuation_date", 
  rv."Pre_capex_long_term",
  rv."Pre_capex_vacant",
  rv."Post_capex",
  rv."Post_capex_residential"
FROM "Resource"."Resource_value" rv
  INNER JOIN "Resource"."Resource" r ON r.id = rv."Resource_id"
ORDER BY 2, 1
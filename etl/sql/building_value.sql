SELECT
  bv.id, 
  b."Code" as "building_id", 
  bv."Valuation_date" AS "valuation_date", 
  bv."Valuation_type" AS "valuation_type",
  bv."Pre_capex_long_term" AS "pre_capex_long_term", 
  bv."Pre_capex_vacant" AS "pre_capex_vacant", 
  bv."Post_capex" AS "post_capex", 
  bv."ECO_valuation" AS "eco_valuation", 
  bv."ECO_rent_update" AS "eco_rent_update", 
  bv."ECO_refinance" AS "eco_refinance", 
  bv."RICS_valuation" AS "rics_valuation"
FROM "Building"."Building_value" bv
  INNER JOIN "Building"."Building" b ON b.id = bv."Building_id"
;
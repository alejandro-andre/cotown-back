SELECT
  b."Code", 
  bv."Valuation_date", 
  bv."Pre_capex_long_term", 
  bv."Pre_capex_vacant", 
  bv."Post_capex", 
  bv."ECO_valuation", 
  bv."ECO_rent_update", 
  bv."ECO_refinance", 
  bv."RICS_valuation"
FROM "Building"."Building_value" bv
  INNER JOIN "Building"."Building" b ON b.id = bv."Building_id"
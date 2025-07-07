SELECT 
  b."Code", bt."Name" AS "Type", b."Name", s."Name" AS "Segment", b."Start_date", b."Estabilised_date", 
  b."Address", b."Zip", b."Lat_lon", b."Order", 
  b."Description", b."Description_en",
  b."Details", b."Details_en",
  d."Name" AS "District", l."Name" AS "City", p."Name" AS "Province", c."Name" AS "Country",
  b."Management_fee",
  b."Gate_mac", b."Gate_phone", b."Gate_url",
  b."Wifi_key", b."Wifi_ssid",
  (SELECT bv."Valuation_date"
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."Pre_capex_long_term" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "Vicente_date",
  (SELECT bv."Pre_capex_long_term"
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."Pre_capex_long_term" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "Pre_capex_long_term",
  (SELECT bv."Pre_capex_vacant" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."Pre_capex_vacant" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "Pre_capex_vacant",
  (SELECT bv."Post_capex" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."Post_capex" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "Post_capex",
  (SELECT bv."Valuation_date"
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."ECO_valuation" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "ECO_date",
  (SELECT bv."ECO_valuation" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."ECO_valuation" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "ECO_valuation",
  (SELECT bv."ECO_rent_update" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."ECO_rent_update" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "ECO_rent_update",
  (SELECT bv."ECO_refinance" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."ECO_refinance" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "ECO_refinance",
  (SELECT bv."Valuation_date" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."RICS_valuation" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "RICS_date",
  (SELECT bv."RICS_valuation" 
   FROM "Building"."Building_value" bv 
   WHERE bv."Building_id" = b.id AND bv."RICS_valuation" IS NOT NULL 
   ORDER BY bv."Valuation_date" DESC 
   LIMIT 1) AS "RICS_valuation"
FROM "Building"."Building" b
  INNER JOIN "Building"."Building_type" bt ON bt.id = b."Building_type_id"
  INNER JOIN "Auxiliar"."Segment" s ON s.id = b."Segment_id"
  INNER JOIN "Geo"."District" d ON d.id = b."District_id"
  INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
  INNER JOIN "Geo"."Province" p ON p.id = l."Province_id"
  INNER JOIN "Geo"."Country" c ON c.id = p."Country_id";
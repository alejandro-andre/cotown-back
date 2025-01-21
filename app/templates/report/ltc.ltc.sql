SELECT 
  bu."Code" AS "Building", 
  r."Code" AS "Resource", rs."Name" AS "Status_name", l."Name" AS "City", r."Area", r. "Places", 
  COALESCE(bo."Rent", 0) + COALESCE(bo."Extras", 0) AS "Current_rent",
  r."Pre_capex_long_term", r."Pre_capex_vacant", r."Post_capex", r."Capex",
  g."Name_en" AS "Gender", 
  c."Birth_date",
  etl.labels[array_position(et.values, bo."Pending_subrogation"::text)]::text AS "Pending_subrogation",
  bo."Date_to",
  bo."Date_estimated",
  CASE
    WHEN bo."Contribution_chance" THEN 'Yes'
    ELSE 'No'
  END AS "Contribution_chance", 
  bo."Contribution_percent", bo."Contribution_recommended", bo."Contribution_asking", 
  bo."Contribution_proposal", bo."Contribution_proposed_date", bo."Contribution_comments",
  bo."Comments",
  CASE
    WHEN bo."Date_estimated" IS NULL AND bo."Date_to" IS NULL THEN 'LTNC'
    WHEN bo."Date_estimated" IS NOT NULL AND bo."Date_to" IS NULL THEN 'LTC'
    ELSE 'FTC'
  END AS "Tenancy_type"
FROM "Resource"."Resource" r
  INNER JOIN "Booking"."Booking_other" bo ON bo."Resource_id" = r.id
  INNER JOIN "Billing"."Product" p ON p.id = bo."Product_id" 
  LEFT JOIN "Resource"."Resource_status" rs ON rs.id = r."Status_id"
  LEFT JOIN "Building"."Building" bu ON bu.id = r."Building_id" 
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id" 
  LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id" 
  LEFT JOIN "Customer"."Customer" c ON c.id = bo."Customer_id" 
  LEFT JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id"
  INNER JOIN "Models"."EnumType" et ON et.id = 24
  INNER JOIN "Models"."EnumTypeLabel" etl ON etl.container = et.id AND etl.locale = 'en_US'
WHERE p."Name" LIKE 'Renta (LAU)%'
AND r."Status_id" IN (2, 3)
ORDER BY "Tenancy_type" DESC, 1
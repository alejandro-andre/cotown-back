SELECT 
  bu."Code" AS "Building", 
  r."Code" AS "Resource", rs."Name" AS "Status_name", l."Name" AS "City", r."Area", r. "Places", 
  COALESCE(bo."Rent", 0) + COALESCE(bo."Extras", 0) AS "Current_rent",
  r."Pre_capex_long_term", r."Pre_capex_vacant", r."Post_capex", r."Post_capex_residential", r."Capex",
  r."SAP_code",
  g."Name_en" AS "Gender", 
  c."Birth_date",
  etsl.labels[array_position(ets.values, bo."Pending_subrogation"::text)]::text AS "Pending_subrogation",
  etnl.labels[array_position(etn.values, bo."Negotiation"::text)]::text AS "Negotiation",
  bo."Date_to",
  bo."Date_estimated",
  CASE
    WHEN bo."Contribution_chance" THEN 'Yes'
    ELSE 'No'
  END AS "Contribution_chance", 
  bo."Contribution_percent" / 100.0 AS "Contribution_percent", 
  bo."Contribution_recommended", 
  bo."Contribution_asking", 
  bo."Contribution_proposal", 
  bo."Contribution_proposed_date", 
  bs."Name_en" AS "Substatus_name",
  CASE
    WHEN bo."Date_estimated" IS NULL AND bo."Date_to" IS NULL THEN 'LTNC'
    WHEN bo."Date_estimated" IS NOT NULL AND bo."Date_to" IS NULL THEN 'LTC'
    ELSE 'FTC'
  END AS "Tenancy_type"
FROM "Resource"."Resource" r
  INNER JOIN "Booking"."Booking_other" bo ON bo."Resource_id" = r.id
  INNER JOIN "Booking"."Booking_subtype" bs ON bs.id = bo."Substatus_id" 
  INNER JOIN "Billing"."Product" p ON p.id = bo."Product_id" 
  LEFT JOIN "Resource"."Resource_status" rs ON rs.id = r."Status_id"
  LEFT JOIN "Building"."Building" bu ON bu.id = r."Building_id" 
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id" 
  LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id" 
  LEFT JOIN "Customer"."Customer" c ON c.id = bo."Customer_id" 
  LEFT JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id"
  INNER JOIN "Models"."EnumType" ets ON ets.id = 24
  INNER JOIN "Models"."EnumType" etn ON etn.id = 28
  INNER JOIN "Models"."EnumTypeLabel" etsl ON etsl.container = ets.id AND etsl.locale = 'en_US'
  INNER JOIN "Models"."EnumTypeLabel" etnl ON etnl.container = etn.id AND etnl.locale = 'en_US'
WHERE r."Resource_type" = 'piso'
  AND r."Status_id" IN (2, 3)
  AND bo."Substatus_id" <> 6
ORDER BY "Tenancy_type" DESC, 1
;
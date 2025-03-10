SELECT 
  b.id, 
  cr."Name_en" AS "Reason",
  s."Name" AS "school",
  sc."Name_en" AS "school_type",
  b."Status" AS "status",
  bw."Name_en" AS "who",
  br."Name_en" AS "referral",
  bc."Name_en" AS "channel",
  a."Name" AS "agent",
  c."Name" AS "customer",
  c."Email" AS "email",
  c."Phones" AS "phones",
  c."Birth_date" AS "birth_date",
  g."Code" AS "gender",
  cn."Name_en" AS "nationality",
  cn."Continent" AS "continent",
  l."Name_en" AS "language",
  c."Created_at" AS "first_contact",
  b."Request_date" AS "request_date",
  b."Confirmation_date" AS "confirmation_date",
  r."Code" as "resource", 
  b."Rent" AS "rent",
  b."Services" AS "services",
  (SELECT SUM(bp."Rent") FROM "Booking"."Booking_price" bp WHERE bp."Booking_id" = b.id) AS "total_rent",
  (SELECT SUM(bp."Services") FROM "Booking"."Booking_price" bp WHERE bp."Booking_id" = b.id) AS "total_services",
  b."Limit" AS "limit",
  b."Commision" AS "direct_cost",
  b."Date_from" AS "date_from",
  b."Date_to" AS "date_to",
  b."Check_in" AS "check_in",
  b."Check_out" AS "check_out",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  COALESCE(t."Value", 0) / 100 AS "tax",
  COALESCE(b."Booking_fee_actual", 0) AS "booking_fee",
  r."Management_fee" / 100 AS "management_fee"
FROM "Booking"."Booking" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  LEFT JOIN "Booking"."Customer_reason" cr ON cr.id = b."Reason_id"
  LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Building"."Building" bu on bu.id = r."Building_id" 
  LEFT JOIN "Building"."Building_type" bt ON bt.id = bu."Building_type_id" 
  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id" 
  LEFT JOIN "Geo"."Country" cn ON cn.id = c."Nationality_id"
  LEFT JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id"
  LEFT JOIN "Auxiliar"."Language" l ON l.id = c."Language_id"
  LEFT JOIN "Auxiliar"."School" s ON s.id = b."School_id" 
  LEFT JOIN "Auxiliar"."School_category" sc ON sc.id = s."Category" 
  LEFT JOIN "Booking"."Booking_who" bw ON bw.id = b."Booking_who_id"
  LEFT JOIN "Booking"."Booking_referral" br ON br.id = b."Booking_referral_id"
  LEFT JOIN "Booking"."Booking_channel" bc ON bc.id = b."Booking_channel_id"
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
ORDER BY 1
;
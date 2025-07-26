SELECT 
  b.id,
  b."Status",
  b."Request_date",
  b."Confirmation_date",
  b."Date_from",
  b."Date_to",
  b."Check_in",
  b."Check_out",
  b."Rent",
  b."Services",
  c."Name" AS "Name",
  c."Email" AS "Email",
  c."Phones" AS "Phones",
  c."Birth_date",
  c."Created_at",
  g."Code" AS "Gender",
  co."Name" AS "Nationality",
  co."Continent" AS "Continent",
  l."Name" AS "Language",
  bw."Name" AS "Booking_who",
  br."Name" AS "Booking_referral",
  bc."Name" AS "Booking_channel",
  a."Name" AS "Agent",
  CASE
  	WHEN s.id > 1 THEN s."Name"
  	ELSE s."Name" || ' - ' || b."Other_school"
  END AS "School",
  r."Code" AS "Resource",
  rpt."Name" AS "Place_type",
  bu."Name" AS "Building",
  se."Name" as "Segment",
  p."Name" AS "Owner",
  lo."Name" AS "Location",
  lo."Code" AS "Location_code"
FROM "Booking"."Booking" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
  LEFT JOIN "Building"."Building" bu ON bu.id = r."Building_id" 
  LEFT JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
  LEFT JOIN "Geo"."Country" co ON co.id = c."Nationality_id"
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id" 
  LEFT JOIN "Geo"."Location" lo ON lo.id = d."Location_id" 
  LEFT JOIN "Booking"."Booking_channel" bc ON bc.id = b."Booking_channel_id" 
  LEFT JOIN "Booking"."Booking_referral" br ON br.id = b."Booking_referral_id" 
  LEFT JOIN "Booking"."Booking_who" bw ON bw.id = b."Booking_who_id" 
  LEFT JOIN "Auxiliar"."Segment" se ON se.id = bu."Segment_id" 
  LEFT JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id" 
  LEFT JOIN "Auxiliar"."School" s ON s.id = b."School_id"
  LEFT JOIN "Auxiliar"."Language" l ON l.id = c."Language_id" 
ORDER BY 1
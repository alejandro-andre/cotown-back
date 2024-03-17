SELECT DISTINCT ON (c.id)
	b.id,
	c."Name",
	c."Email",
	c."Phones",
	TO_CHAR(c."Birth_date", 'YYYY-MM-DD') AS "Birth_date",
	EXTRACT(YEAR FROM age(c."Birth_date")) AS "Age",
	g."Name" AS "Gender",
	co."Name" AS "Nationality",
	s."Name" AS "School",
	c."Lang" AS "Language",
	TO_CHAR(b."Request_date", 'YYYY-MM-DD') AS "Request_date",
	TO_CHAR(b."Confirmation_date", 'YYYY-MM-DD') AS "Confirmation_date",
	CASE WHEN "Confirmation_date" IS NOT NULL THEN 'win' ELSE '' END AS "Tags",
	bc."Name" AS "Origin",
	br."Name" AS "Suborigin",
	TO_CHAR(b."Date_from", 'YYYY-MM-DD') AS "Date_from",
	TO_CHAR(b."Date_to", 'YYYY-MM-DD') AS "Date_to",
	TO_CHAR(b."Check_in", 'YYYY-MM-DD') AS "Check_in",
	TO_CHAR(b."Check_out", 'YYYY-MM-DD') AS "Check_out",
	l."Name" AS "City",
	substring(r."Code",1, 6) AS "Building",
	substring(r."Code",8, 5) AS "Flat",
	substring(r."Code",14, 9) AS "Place",
	b."Rent",
	b."Services",
	b."Booking_fee",
	sums."Total_rent",
	sums."Total_services",
	sums."Management_fee",
	see."Name" AS "End_brand",
	seo."Name" AS "Origin_brand",
	'B2C' AS "Lead_type",
	b."Status"
FROM "Booking"."Booking" b
  INNER JOIN "Booking"."Booking_channel" bc ON bc.id = b."Booking_channel_id" 
  INNER JOIN "Booking"."Booking_referral" br ON br.id = b."Booking_referral_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bub ON bub.id = r."Building_id" 
  INNER JOIN "Building"."Building" bur ON bur.id = b."Building_id" 
  INNER JOIN "Geo"."District" d ON d.id = bub."District_id" 
  INNER JOIN "Geo"."Location" l ON l.id = d."Location_id" 
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
  INNER JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id"
  INNER JOIN "Geo"."Country" co ON co.id = c."Nationality_id"
  INNER JOIN "Auxiliar"."School" s ON s.id = b."School_id"
  INNER JOIN "Auxiliar"."Segment" see ON see.id = bub."Segment_id"  
  INNER JOIN "Auxiliar"."Segment" seo ON seo.id = bur."Segment_id"
  INNER JOIN (
	SELECT 
	  bp."Booking_id", 
	  SUM(bp."Rent") AS "Total_rent", 
	  SUM(bp."Rent" / (1 + COALESCE(t."Value", 0) / 100) * bu."Management_fee" / 100) AS "Management_fee", 
	  SUM(bp."Services") AS "Total_services"
	FROM "Booking"."Booking_price" bp
	  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
	  INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id"
	  INNER JOIN "Building"."Building_type" bt ON bt.id = bu."Building_type_id" 
	  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id" 
	WHERE "Status" NOT IN ('solicitud','alternativas','alternativaspagada','descartada','descartadapagada','cancelada')
GROUP BY 1) sums ON sums."Booking_id" = b.id
WHERE "Status" NOT IN ('solicitud','alternativas','alternativaspagada','descartada','descartadapagada','cancelada')
  AND (
	b."Created_at" >= %(fdesde)s OR 
	b."Updated_at" >= %(fdesde)s OR
	c."Created_at" >= %(fdesde)s OR
	c."Updated_at" >= %(fdesde)s
  )
ORDER BY c.id, b.id DESC
;
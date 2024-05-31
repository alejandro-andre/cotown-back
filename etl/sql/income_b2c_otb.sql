SELECT 
  CONCAT('COR-', bp.id) AS "id",
  b.id AS "doc_id",
  'otb' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  'Monthly rent' AS "product",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN (bp."Rent" + COALESCE(bp."Rent_discount", 0)) / 1.1
  	ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
  END AS "amount",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Rent"/ 1.1
  	ELSE bp."Rent"
  END AS "rate",
  'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative' 
    ELSE 'OTB' 
  END AS "data_type",
  dtp."Name_en" AS "discount_type"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')

UNION

SELECT 
  CONCAT('COS-', bp.id) AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  CASE
    WHEN r."Service_id" = r."Owner_id" THEN 'Monthly rent'
    ELSE 'Monthly services'
  END "product",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN (bp."Services" + COALESCE(bp."Services_discount", 0)) / 1.1
  	ELSE bp."Services" + COALESCE(bp."Services_discount", 0)
  END AS "amount",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Services"/ 1.1
  	ELSE bp."Services"
  END AS "rate",
  'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative' 
    ELSE 'OTB' 
  END AS "data_type",
  dtp."Name_en" AS "discount_type"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
  AND bp."Services" > 0
;
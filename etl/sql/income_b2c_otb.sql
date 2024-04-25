SELECT 
  CONCAT('COR-', bp.id) AS "id",
  b.id AS "doc_id",
  'otb' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  'Renta mensual' AS "product",
  bp."Rent" + COALESCE(bp."Rent_discount", 0) AS "amount", 
  bp."Rent" AS "rate", 
  'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentativa' 
    ELSE 'OTB' 
  END AS "data_type"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
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
    WHEN r."Service_id" = r."Owner_id" THEN 'Renta mensual'
    ELSE 'Servicios mensuales'
  END "product",
  bp."Services" + COALESCE(bp."Services_discount", 0) AS "amount", 
  bp."Services" AS "rate", 
  'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentativa' 
    ELSE 'OTB' 
  END AS "data_type"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
  AND bp."Services" > 0
;
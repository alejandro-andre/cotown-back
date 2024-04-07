SELECT DISTINCT ON (bp.id) 
  CONCAT('BOR-', bp.id) AS "id",
  b.id as "doc_id",
  'otb' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  r."Code" AS "resource",
  'Renta mensual' AS "product",
  b."Rooms" * bp."Rent" AS "amount", 
  b."Rooms" * bp."Rent" AS "rate", 
  0 AS discount,
  'B2C' AS "income_type",
  'OTB' AS "data_type"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('grupoconfirmado', 'inhouse') 

UNION

SELECT DISTINCT ON (bp.id) 
  CONCAT('BOS-', bp.id) AS "id",
  b.id as "doc_id",
  'otb' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  r."Code" AS "resource",
  'Servicios mensuales' AS "product",
  bp."Services" AS "amount", 
  bp."Services" AS "rate", 
  0 AS discount,
  'B2B' AS "income_type",
  'OTB' AS "data_type"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('grupoconfirmado', 'inhouse') 
  AND bp."Services" > 0
;
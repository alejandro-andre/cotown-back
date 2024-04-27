(
WITH 
"Rooms" AS (
	SELECT bgr."Booking_id" AS "id", r."Owner_id", r."Service_id", p."Document", SUBSTRING(MIN(r."Code"), 1, 12) AS "Code"
	FROM "Booking"."Booking_group_rooming" bgr 
    INNER JOIN "Resource"."Resource" r ON r.id = bgr."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
    GROUP BY 1, 2, 3, 4
)
SELECT 
  CONCAT('BOR', bp.id) AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  r."Document" AS "provider",
  b."Payer_id" AS "customer",
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  'Renta mensual' AS "product",
  b."Rooms" * bp."Rent" AS "amount",
  b."Rooms" * bp."Rent" AS "rate", 
  'B2B' AS "income_type",
  CASE
    WHEN b."Status" IN ('grupobloqueado') THEN 'Tentativa' 
    ELSE 'OTB' 
  END AS "data_type"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Rooms" r on r.id = b.id 
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" <> 'cancelada'
)  
UNION
(
WITH 
"Rooms" AS (
	SELECT bgr."Booking_id" AS "id", r."Owner_id", r."Service_id", p."Document", SUBSTRING(MIN(r."Code"), 1, 12) AS "Code"
	FROM "Booking"."Booking_group_rooming" bgr 
    INNER JOIN "Resource"."Resource" r ON r.id = bgr."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
    GROUP BY 1, 2, 3, 4
)
SELECT 
  CONCAT('BOS', bp.id) AS "id",
  b.id AS "doc_id",
  '-'AS "doc_type",
  bp."Booking_id" AS "booking",
  bp."Rent_date" AS "date",
  r."Document" AS "provider",
  b."Payer_id" AS "customer",
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  CASE
    WHEN r."Owner_id" = r."Service_id" THEN 'Renta mensual'
    ELSE 'Servicios mensuales'
  END "product",
  b."Rooms" * bp."Services" AS "amount", 
  b."Rooms" * bp."Services" AS "rate", 
  'B2B' AS "income_type",
  CASE
    WHEN b."Status" IN ('grupoconfirmado', 'inhouse') THEN 'OTB' 
    ELSE 'Tentativa' 
  END AS "data_type"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Rooms" r on r.id = b.id 
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" <> 'cancelada'
);
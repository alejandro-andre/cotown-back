(
WITH 
"Rooms" AS (
	SELECT bgr."Booking_id" AS "id", r."Owner_id", r."Service_id", p."Document", r."Code", bgr.id as "rid"
	FROM "Booking"."Booking_group_rooms" bgr 
    INNER JOIN "Resource"."Resource" r ON r.id = bgr."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
)
SELECT 
  CONCAT('IBOR', bp.id, r."rid") AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  'G' || bp."Booking_id"::text AS "booking",
  a."Name" AS "marketplace",
  bp."Rent_date" AS "date",
  r."Document" AS "provider",
  b."Payer_id" AS "customer",
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  'Monthly rent' AS "product",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Rent" / 1.1
  	ELSE bp."Rent"
  END AS "amount",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Rent" / 1.1
  	ELSE bp."Rent"
  END AS "rate",
  NULL AS "price",
  --'B2B' AS "income_type",
  CASE
    WHEN b."Status" IN ('grupobloqueado') THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  NULL AS "discount_type",
  b."Book_type"::text AS "book_type",
  b."Limit_type"::text AS "limit_type"
FROM "Booking"."Booking_group_price" bp
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id"
  INNER JOIN "Booking"."Booking_group_rooms" br on b.id = br."Booking_id"
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"
  INNER JOIN "Rooms" r on r.id = b.id
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
WHERE bp."Rent_date" >= CURRENT_DATE
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" <> 'cancelada'
)
UNION
(
WITH
"Rooms" AS (
	SELECT bgr."Booking_id" AS "id", r."Owner_id", r."Service_id", p."Document", r."Code", bgr.id AS "rid"
	FROM "Booking"."Booking_group_rooms" bgr
    INNER JOIN "Resource"."Resource" r ON r.id = bgr."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
)
SELECT
  CONCAT('IBOS', bp.id, r."rid") AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  'G' || bp."Booking_id"::text AS "booking",
  a."Name" AS "marketplace",
  bp."Rent_date" AS "date",
  r."Document" AS "provider",
  b."Payer_id" AS "customer",
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  CASE
    WHEN r."Owner_id" = r."Service_id" THEN 'Monthly rent'
    ELSE 'Monthly services'
  END "product",
  CASE
  	WHEN bu."Building_type_id" = 3 THEN bp."Services" / 1.1
  	ELSE bp."Services"
  END AS "amount",
  CASE
  	WHEN bu."Building_type_id" = 3 THEN bp."Services" / 1.1
  	ELSE bp."Services"
  END AS "rate",
  NULL AS "price",
  --'B2B' AS "income_type",
  CASE
    WHEN b."Status" IN ('grupoconfirmado', 'inhouse') THEN 'OTB'
    ELSE 'Tentative'
  END AS "data_type",
  NULL AS "discount_type",
  b."Book_type"::text AS "book_type",
  b."Limit_type"::text AS "limit_type"
FROM "Booking"."Booking_group_price" bp
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id"
  INNER JOIN "Booking"."Booking_group_rooms" br on b.id = br."Booking_id"
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"
  INNER JOIN "Rooms" r on r.id = b.id
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
WHERE bp."Rent_date" >= CURRENT_DATE
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" <> 'cancelada'
);
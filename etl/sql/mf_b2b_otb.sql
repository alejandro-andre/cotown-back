WITH 
"Rooms" AS (
	SELECT bgr."Booking_id" AS "id", r."Owner_id", r."Service_id", p."Document", (r."Code"), r."Management_fee", bgr.id AS "rid"
	FROM "Booking"."Booking_group_rooms" bgr 
    INNER JOIN "Resource"."Resource" r ON r.id = bgr."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
)
SELECT 
  CONCAT('BOM', bp.id, r.rid) AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  'B' || bp."Booking_id"::text AS "booking",
  bp."Rent_date" AS "date",
  r."Document" AS "provider",
  b."Payer_id" AS "customer",
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  'Management fee' AS "product",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Rent" / 1.1
  	ELSE bp."Rent"
  END * r."Management_fee" / 100 AS "amount",
  CASE 
  	WHEN bu."Building_type_id" = 3 THEN bp."Rent" / 1.1
  	ELSE bp."Rent"
  END * r."Management_fee" / 100 AS "rate",
  NULL AS "price",
  --'B2B' AS "income_type",
  CASE
    WHEN b."Status" IN ('grupobloqueado') THEN 'Tentative'
    ELSE 'OTB' 
  END AS "data_type",
  NULL AS "discount_type"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Rooms" r on r.id = b.id 
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" <> 'cancelada'
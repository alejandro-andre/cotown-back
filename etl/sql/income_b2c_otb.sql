-- Rent
SELECT 
  CONCAT('ICOR', bp.id) AS "id",
  b.id AS "doc_id",
  'otb' AS "doc_type",
  'C' || bp."Booking_id"::text AS "booking",
  a."Name" AS "marketplace",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN b."Master_id" IS NOT NULL THEN 'GROUP'
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
  	WHEN bu."Building_type_id" = 3 THEN COALESCE(bp."Rent_rack", bp."Rent") / 1.1
  	ELSE COALESCE(bp."Rent_rack", bp."Rent")
  END AS "rate",
  "Rent_rack" AS "price",
  --'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  dtp."Name_en" AS "discount_type",
  COALESCE(NULLIF(b."Book_type"::text, ''), 'libre') AS "book_type",
  COALESCE(NULLIF(b."Limit_type"::text, ''), 'libre') AS "limit_type"
FROM "Booking"."Booking_price" bp
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id"
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
WHERE bp."Rent_date" >= CURRENT_DATE
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')

UNION

-- Services
SELECT
  CONCAT('ICOS', bp.id) AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  'C' || bp."Booking_id"::text AS "booking",
  a."Name" AS "marketplace",
  bp."Rent_date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN b."Master_id" IS NOT NULL THEN 'GROUP'
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
  "Services_rack" AS "price",
  --'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  dtp."Name_en" AS "discount_type",
  COALESCE(NULLIF(b."Book_type"::text, ''), 'libre') AS "book_type",
  COALESCE(NULLIF(b."Limit_type"::text, ''), 'libre') AS "limit_type"
FROM "Booking"."Booking_price" bp
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id"
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
WHERE bp."Rent_date" >= CURRENT_DATE
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
  AND bp."Services" > 0

UNION

-- Other non recurring
SELECT
  CONCAT('ICOON', bs.id) AS "id",
  bs."Booking_id" AS "doc_id",
  '-' AS "doc_type",
  'C' || bs."Booking_id"::text AS "booking",
  a."Name" AS "marketplace",
  GREATEST(CURRENT_DATE, bs."Billing_date_from") AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN b."Master_id" IS NOT NULL THEN 'GROUP'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  pr."Name_en" AS "product",
  bs."Amount" / (1 + (t."Value" / 100)) AS "amount",
  bs."Amount" / (1 + (t."Value" / 100)) AS "rate",
  bs."Amount" / (1 + (t."Value" / 100)) AS "price",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  NULL AS "discount_type",
  COALESCE(NULLIF(b."Book_type"::text, ''), 'libre') AS "book_type",
  COALESCE(NULLIF(b."Limit_type"::text, ''), 'libre') AS "limit_type"
FROM "Booking"."Booking_service" bs
  INNER JOIN "Booking"."Booking" b ON b.id = bs."Booking_id"
  INNER JOIN "Provider"."Provider" p ON p.id = 10
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Billing"."Product" pr ON pr.id = bs."Product_id"
  INNER JOIN "Billing"."Tax" t ON t.id = bs."Tax_id"
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
WHERE bs."Invoice_services_id" IS NULL
  AND bs."Billing_date_from" > CURRENT_DATE
  AND bs."Extra_type" <> 'recurrente'
  AND bs."Amount" > 0
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')

UNION

-- Other recurring
SELECT
  CONCAT('ICOOR', bs.id, to_char(d.dt, 'YYYYMM')) AS "id",
  bs."Booking_id" AS "doc_id",
  '-' AS "doc_type",
  'C' || bs."Booking_id"::text AS "booking",
  NULL AS "marketplace",
  d.dt AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN b."Master_id" IS NOT NULL THEN 'GROUP'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  pr."Name_en" AS "product",
  bs."Amount" / (1 + (t."Value" / 100)) AS "amount",
  bs."Amount" / (1 + (t."Value" / 100)) AS "rate",
  bs."Amount" / (1 + (t."Value" / 100)) AS "price",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  NULL AS "discount_type",
  COALESCE(NULLIF(b."Book_type"::text, ''), 'libre') AS "book_type",
  COALESCE(NULLIF(b."Limit_type"::text, ''), 'libre') AS "limit_type"
FROM "Booking"."Booking_service" bs
  JOIN "Booking"."Booking" b ON b.id = bs."Booking_id"
  JOIN "Provider"."Provider" p ON p.id = 10
  JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  JOIN "Billing"."Product" pr ON pr.id = bs."Product_id"
  JOIN "Billing"."Tax" t ON t.id = bs."Tax_id"
  JOIN LATERAL (
    SELECT generate_series(
      date_trunc('month', GREATEST(CURRENT_DATE, bs."Billing_date_from")),
      date_trunc('month', bs."Billing_date_to"),
      interval '1 month'
    ) AS dt
) d ON TRUE
WHERE bs."Invoice_services_id" IS NULL
  AND bs."Extra_type" = 'recurrente'
  AND bs."Amount" > 0
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
;
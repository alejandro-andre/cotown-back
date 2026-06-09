SELECT 
  CONCAT('ICOM', bp.id) AS "id",
  b.id AS "doc_id",
  'otb' AS "doc_type",
  'C' || bp."Booking_id"::text AS "booking",
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
  'Management fee' AS "product",
  ROUND(
    CASE 
  	  WHEN bu."Building_type_id" = 3 THEN ((COALESCE(bp."Rent", 0) + COALESCE(bp."Rent_discount", 0)) / 1.1)
  	  ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
    END 
    *
    CASE 
      WHEN b."Cleaning_freq" = 'no' THEN COALESCE(r."Management_fee_no_cleaning", 0) / 100 
      WHEN b."Cleaning_freq" = 'semanal' THEN COALESCE(r."Management_fee_weekly", 0) / 100 
      WHEN b."Cleaning_freq" = 'quincenal' THEN COALESCE(r."Management_fee_biweekly", 0) / 100 
      WHEN b."Cleaning_freq" = 'mensual' THEN COALESCE(r."Management_fee_monthly", 0) / 100 
      ELSE COALESCE(r."Management_fee", 0) / 100 
    END, 4
  ) AS "amount",
  0 AS "rate",
  NULL AS "price",
  --'B2C' AS "income_type",
  CASE
    WHEN b."Status" = 'confirmada' THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  NULL AS "discount_type",
  b."Book_type"::text AS "book_type",
  b."Limit_type"::text AS "limit_type"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
WHERE bp."Rent_date" >= '2024-01-01'
  AND bp."Invoice_rent_id" IS NULL AND bp."Invoice_services_id" IS NULL
  AND b."Status" IN ('confirmada', 'firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
SELECT 
  CONCAT('CRM', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  i."Booking_id" AS "booking",
  i."Issued_date" AS "date", 
  p."Document" AS "provider",
  i."Customer_id" AS "customer",
  r."Code" AS "resource",
  'Management fee' AS "product",
  il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "amount",
  il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "rate",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  --'B2C' AS "income_type",
  'Real' AS "data_type",
  NULL AS "discount_type"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND i."Provider_id" <> 1 
  AND i."Booking_id" IS NOT NULL
  AND i."Bill_type" <> 'recibo'
UNION ALL
SELECT 
  CONCAT('BRM', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  i."Booking_group_id" AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider",
  i."Customer_id" AS "customer",
  r."Code" AS "resource",
  'Management fee' AS "product",
  il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "amount",
  il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "rate",
  'GROUP' AS "stay_length",
  --'B2B' AS "income_type",
  'Real' AS "data_type",
  NULL AS "discount_type"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
  INNER JOIN "Resource"."Resource" r on r.id = il."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND i."Provider_id" <> 1 
  AND i."Booking_group_id" IS NOT NULL
  AND i."Bill_type" <> 'recibo'
ORDER BY 4, 2
SELECT
  CONCAT('LRX', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  'L' || b.id::text AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  i."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE 
	  WHEN b."Booking_type" = 'lau' THEN 'LAU'
	  ELSE 'RETAIL'
  END AS "stay_length",
  pr."Name_en" AS "product",
  il."Amount" / (1 + (t."Value" / 100)) AS "amount",
  il."Amount" / (1 + (t."Value" / 100)) AS "rate",
  'Real' AS "data_type",
  '' AS "discount_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking_other" b ON b.id = i."Booking_other_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id" 
WHERE i."Issued_date" >= '2024-01-01'
;


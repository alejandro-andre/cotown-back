SELECT
  CONCAT('BRX', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  'G' || b.id::text AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  i."Customer_id" AS "customer",
  pr."Name_en" AS "product",
  il."Amount" / (1 + (t."Value" / 100)) AS "amount",
  CASE 
    WHEN i."Rectified" OR i."Bill_type" = 'rectificativa' THEN il."Amount" / (1 + (t."Value" / 100))
    WHEN pr.id = 1 THEN il."Amount" / (1 + (t."Value" / 100))
    WHEN pr."Product_type_id" = 3 THEN COALESCE(bp."Rent", il."Amount") / (1 + (t."Value" / 100))
    WHEN pr."Product_type_id" <> 3 THEN COALESCE(bp."Services", il."Amount") / (1 + (t."Value" / 100))
  END AS "rate",
  --'B2B' AS "income_type",
  'Real' AS "data_type",
  NULL AS "discount_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking_group" b ON b.id = i."Booking_group_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = il."Resource_id" 
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id" 
  LEFT JOIN "Booking"."Booking_price" bp ON bp."Invoice_rent_id" = i.id 
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND (pr."Product_type_id" <> 2 OR i."Bill_type" <> 'recibo')
;
SELECT
  CONCAT('BRX', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  b.id AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  r."Code" AS "resource",
  'GROUP' AS "stay_length",
  i."Customer_id" AS "customer",
  CASE
    WHEN pr."Product_type_id" > 3 AND i."Provider_id" <> 1 THEN 'Renta mensual'
    ELSE pr."Name"
  END "product",
  il."Amount" AS "amount",
  CASE 
    WHEN pr.id = 1 THEN il."Amount"
	  WHEN pr."Product_type_id" = 3 THEN COALESCE(bp."Rent", il."Amount") 	
	  WHEN pr."Product_type_id" <> 3 THEN COALESCE(bp."Services", il."Amount") 	
  END AS "rate",
  'B2B' AS "income_type",
  'Real' AS "data_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking_group" b ON b.id = i."Booking_group_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = il."Resource_id" 
  LEFT JOIN "Booking"."Booking_price" bp ON bp."Invoice_rent_id" = i.id 
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND pr."Product_type_id" <> 2
;
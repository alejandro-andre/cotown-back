SELECT
  CONCAT('F-', i.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  b.id AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  r."Code" AS "resource",
  pr."Name" AS "product",
  il."Amount" AS "amount",
  CASE 
    WHEN pr.id = 1 AND i."Bill_type" = 'factura' THEN b."Booking_fee"
	WHEN pr."Product_type_id" = 1 THEN il."Amount"
	WHEN pr."Product_type_id" = 1 THEN COALESCE(bp."Rent", il."Amount") 	
	WHEN pr."Product_type_id" = 3 THEN COALESCE(bp."Rent", il."Amount") 	
	WHEN pr."Product_type_id" = 4 THEN COALESCE(bp."Services", il."Amount") 	
  END AS "rate",
  CASE 
    WHEN pr.id = 1 AND i."Bill_type" = 'factura' THEN b."Booking_fee" - il."Amount"
	WHEN pr."Product_type_id" = 1 THEN 0
	WHEN pr."Product_type_id" = 1 THEN COALESCE(bp."Rent", il."Amount") - il."Amount"
	WHEN pr."Product_type_id" = 3 THEN COALESCE(bp."Rent", il."Amount") - il."Amount"
	WHEN pr."Product_type_id" = 4 THEN COALESCE(bp."Services", il."Amount") - il."Amount"
  END AS "discount",
  pt."Name" AS "income_type",
  'Real' AS "data_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking" b ON b.id = i."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  LEFT JOIN "Booking"."Booking_price" bp ON bp."Invoice_rent_id" = i.id 
WHERE i."Issued_date" >= '2024-01-01'
  AND pr."Product_type_id" <> 2
;
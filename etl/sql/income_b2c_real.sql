SELECT
  CONCAT('CRX', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  'C' || b.id::text AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  i."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  pr."Name_en" AS "product",
  il."Amount" / (1 + (t."Value" / 100)) AS "amount",
  CASE 
	  WHEN pr.id = 3 THEN COALESCE(bp."Rent_rack", il."Amount") / (1 + (t."Value" / 100))
	  ELSE 0
  END AS "rate",
  CASE 
    WHEN i."Rectified" OR i."Bill_type" = 'rectificativa' THEN NULL
    WHEN pr."Product_type_id" = 1 THEN b."Booking_fee"
	  WHEN pr."Product_type_id" = 3 THEN bp."Rent_rack"
	  WHEN pr."Product_type_id" > 3 THEN bp."Services_rack"
  END AS "price",
  --'B2C' AS "income_type",
  'Real' AS "data_type",
  CASE 
    WHEN pr."Product_type_id" = 1 THEN dtb."Name_en"
    ELSE dtp."Name_en"
   END AS "discount_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking" b ON b.id = i."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id" 
  LEFT JOIN "Booking"."Booking_price" bp ON bp."Invoice_rent_id" = i.id 
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
  LEFT JOIN "Booking"."Booking_discount_type" dtb ON dtb.id = b."Booking_discount_type_id"
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND (pr."Product_type_id" <> 2 OR i."Bill_type" <> 'recibo')
;
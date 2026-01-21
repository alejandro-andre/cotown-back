(
-- Facturas B2C
SELECT 
  pr."Name" AS "Owner",
  i."Issued_date" AS "Income_date", 
  ''||i."Booking_id" AS "Booking_id", 
  r."Code", 
  b."Date_from", 
  b."Date_to", 
  il."Amount" AS "Amount",
  t."Value" / 100 AS "Tax",
  i."Code" AS "Invoice",
  pd."Name" AS "Product",
  pdt."Name" AS "Product_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN il."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = pd."Product_type_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  LEFT JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
  LEFT JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
WHERE i."Issued" AND (pd."Product_type_id" <> 2 OR i."Bill_type" <> 'recibo') AND i."Booking_id" IS NOT NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s

UNION ALL

-- Facturas B2B
SELECT 
  pr."Name" AS "Owner", 
  i."Issued_date" AS "Income_date", 
  'G'||i."Booking_group_id" AS "Booking_id", 
  bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code",
  b."Date_from", 
  b."Date_to", 
  il."Amount" AS "Amount",
  t."Value" / 100 AS "Tax",
  i."Code" AS "Invoice",
  pd."Name" AS "Product",
  pdt."Name" AS "Product_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN il."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = pd."Product_type_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  LEFT JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
  LEFT JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  LEFT JOIN "Resource"."Resource" r ON r.id = il."Resource_id"
WHERE i."Issued" AND (pd."Product_type_id" <> 2 OR i."Bill_type" <> 'recibo') AND i."Booking_group_id" IS NOT NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s
)
ORDER BY "Owner", "Income_date", "Invoice";
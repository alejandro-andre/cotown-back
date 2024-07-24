(
-- Rentas B2C facturadas
SELECT pr."Name" AS "Owner", EXTRACT(MONTH from i."Issued_date") AS "Month", EXTRACT(YEAR from i."Issued_date") AS "Year",
  i."Booking_id", b."Date_from", b."Date_to", r."Code", c."Name", c."Email",
  il."Amount" AS "Amount",
  t."Value" / 100 AS "Tax",
  CASE 
    WHEN p."Payment_date" IS NULL THEN il."Amount"
    ELSE 0.0
  END AS "Amount_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Payment_status",
  pm."Name" AS "Payment_method", p."Payment_date", i."Code" AS "Invoice",
  CASE WHEN i."Booking_id" IS NOT NULL THEN 'B2C' ELSE '---' END AS "Type",
  pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = pd."Product_type_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  INNER JOIN "Customer"."Customer" c on c.id = i."Customer_id"
  LEFT JOIN "Billing"."Payment" p on p.id = i."Payment_id"
  LEFT JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
  LEFT JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE i."Issued" AND pd."Product_type_id" <> 2 AND i."Booking_group_id" IS NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s

UNION ALL

-- Rentas B2B facturadas
SELECT pr."Name" AS "Owner", EXTRACT(MONTH from i."Issued_date") AS "Month", EXTRACT(YEAR from i."Issued_date") AS "Year",
  i."Booking_group_id", b."Date_from", b."Date_to", bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code", c."Name", c."Email",
  il."Amount" AS "Amount",
  t."Value" / 100 AS "Tax",
  CASE 
    WHEN p."Payment_date" IS NULL THEN il."Amount"
    ELSE 0.0
  END AS "Amount_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Payment_status",
  pm."Name" AS "Payment_method", p."Payment_date", i."Code" AS "Invoice",
  'B2B' AS "Type", pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = pd."Product_type_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  INNER JOIN "Customer"."Customer" c on c.id = i."Customer_id"
  LEFT JOIN "Billing"."Payment" p on p.id = i."Payment_id" 
  LEFT JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
  LEFT JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  LEFT JOIN "Resource"."Resource" r ON r.id = il."Resource_id"
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE i."Issued" AND pd."Product_type_id" <> 2  AND i."Booking_group_id" IS NOT NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s

UNION ALL

-- Rentas B2C no facturadas
SELECT 
  pr."Name" AS "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", r."Code", c."Name", c."Email",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN bp."Rent" + COALESCE(bp."Rent_discount", 0) + bp."Services" + COALESCE(bp."Services_discount", 0)
    ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
  END AS "Amount",
  CASE 
    WHEN bt."Tax_id" IS NOT NULL THEN t."Value" / 100 
    ELSE 0
  END AS "Tax",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN bp."Rent" + COALESCE(bp."Rent_discount", 0) + bp."Services" + COALESCE(bp."Services_discount", 0)
    ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
  END AS "Amount_due",
  'Pending' AS "Payment_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL AS "Invoice",
  'B2C' AS "Type", pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  INNER JOIN "Building"."Building_type" bt ON bt.id = bu."Building_type_id"
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id"
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = 3
  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id"
WHERE bp."Invoice_rent_id" IS NULL
  AND b."Status" IN ('firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision') 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s

UNION ALL

-- Rentas B2B no facturadas
SELECT DISTINCT ON (bp.id)
  pr."Name" AS "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code", c."Name", c."Email",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN b."Rooms" * (bp."Rent" + bp."Services")
    ELSE b."Rooms" * bp."Rent"
  END AS "Amount",
  CASE 
    WHEN bt."Tax_id" IS NOT NULL THEN t."Value" / 100 
    ELSE 0
  END AS "Tax",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN b."Rooms" * (bp."Rent" + bp."Services")
    ELSE b."Rooms" * bp."Rent"
  END AS "Amount_due",
  'Pending' AS "Payment_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL AS "Invoice",
  'B2B' AS "Type", pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b on b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Building"."Building_type" bt ON bt.id = bu."Building_type_id"
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id"
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = 3
  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id"
WHERE bp."Invoice_rent_id" IS NULL 
  AND b."Status" IN ('grupoconfirmado', 'inhouse') 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
UNION ALL

-- Servicios B2C no facturados
SELECT 
  pr."Name" AS "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", r."Code", c."Name", c."Email",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN 0
    ELSE bp."Services" + COALESCE(bp."Services_discount", 0)
  END AS "Amount",
  t."Value" / 100 AS "Tax",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN 0
    ELSE bp."Services" + COALESCE(bp."Services_discount", 0)
  END AS "Amount_due",
  'Pending' AS "Payment_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL AS "Invoice",
  'B2C' AS "Type", pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Billing"."Tax" t ON t.id = 1
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Service_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id"
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = 4
WHERE bp."Invoice_rent_id" IS NULL
  AND b."Status" IN ('firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision') 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
UNION ALL

-- Servicios B2B no facturados
SELECT DISTINCT ON (bp.id)
  pr."Name" AS "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code", c."Name", c."Email",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN 0
    ELSE b."Rooms" * bp."Services"
  END AS "Amount",
  t."Value" / 100 AS "Tax",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN 0
    ELSE b."Rooms" * bp."Services"
  END AS "Amount_due",
  'Pending' AS "Payment_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL AS "Invoice",
  'B2B' AS "Type", pdt."Name" AS "Amount_type",
  CASE WHEN pr."Provider_type_id" = 1 THEN r."Management_fee" / 100 ELSE NULL END AS "Management_fee"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Billing"."Tax" t ON t.id = 1
  INNER JOIN "Booking"."Booking_group" b on b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_group_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Service_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id"
  INNER JOIN "Billing"."Product_type" pdt on pdt.id = 4
WHERE bp."Invoice_rent_id" IS NULL 
  AND b."Status" IN ('grupoconfirmado', 'inhouse') 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
)
ORDER BY "Owner", "Month", "Year", "Code"
;
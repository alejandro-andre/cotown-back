-- Rentas B2C facturadas
(
SELECT pr."Name" as "Owner", EXTRACT(MONTH from i."Issued_date") AS "Month",EXTRACT(YEAR from i."Issued_date") AS "Year",
  i."Booking_id", b."Date_from", b."Date_to", r."Code", c."Name",
  i."Total" AS "Rent",
  CASE 
    WHEN p."Payment_date" IS NULL THEN i."Total"
    ELSE 0.0
  END AS "Rent_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Rent_status",
  pm."Name" AS "Payment_method", p."Payment_date", i."Code" as "Invoice" 
FROM "Billing"."Invoice" i 
  INNER JOIN "Billing"."Invoice_line" il on i.id = il."Invoice_id" 
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Payment" p on p.id = i."Payment_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  INNER JOIN "Customer"."Customer" c on c.id = i."Customer_id" 
  LEFT JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
  LEFT JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE pd."Product_type_id" = 3 AND b.id IS NOT NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s
UNION
-- Rentas B2B facturadas
SELECT pr."Name" as "Owner", EXTRACT(MONTH from i."Issued_date") AS "Month",EXTRACT(YEAR from i."Issued_date") AS "Year",
  i."Booking_group_id", b."Date_from", b."Date_to", bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code", c."Name",
  i."Total" AS "Rent",
  CASE 
    WHEN p."Payment_date" IS NULL THEN i."Total"
    ELSE 0.0
  END AS "Rent_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Rent_status",
  pm."Name" AS "Payment_method", p."Payment_date", i."Code" as "Invoice"
FROM "Billing"."Invoice" i 
  INNER JOIN "Billing"."Invoice_line" il on i.id = il."Invoice_id" 
  INNER JOIN "Billing"."Product" pd on pd.id = il."Product_id" 
  INNER JOIN "Billing"."Payment" p on p.id = i."Payment_id" 
  INNER JOIN "Provider"."Provider" pr on pr.id = i."Provider_id" 
  INNER JOIN "Customer"."Customer" c on c.id = i."Customer_id" 
  LEFT JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
  LEFT JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE pd."Product_type_id" = 3 AND b.id IS NOT NULL 
  AND i."Issued_date" >= %(fdesde)s AND i."Issued_date" < %(fhasta)s AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s
UNION
-- Rentas B2C no facturadas
SELECT 
  pr."Name" as "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", r."Code", c."Name",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN bp."Rent" + COALESCE(bp."Rent_discount", 0) + bp."Services" + COALESCE(bp."Services_discount", 0)
    ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
  END AS "Rent",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN bp."Rent" + COALESCE(bp."Rent_discount", 0) + bp."Services" + COALESCE(bp."Services_discount", 0)
    ELSE bp."Rent" + COALESCE(bp."Rent_discount", 0)
  END AS "Rent_due",
  'Pending' AS "Rent_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL as "Invoice" 
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id"
WHERE bp."Invoice_rent_id" IS NULL 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
UNION
-- Rentas B2B no facturadas
SELECT DISTINCT ON (bp.id)
  pr."Name" as "Owner", EXTRACT(MONTH from bp."Rent_date") AS "Month",EXTRACT(YEAR from bp."Rent_date") AS "Year",
  bp."Booking_id", b."Date_from", b."Date_to", bu."Code"||' ('||b."Rooms"||' plazas)' AS "Code", c."Name",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN b."Rooms" * (bp."Rent" + bp."Services")
    ELSE b."Rooms" * bp."Rent"
  END AS "Rent",
  CASE 
    WHEN r."Owner_id" = r."Service_id" THEN b."Rooms" * (bp."Rent" + bp."Services")
    ELSE b."Rooms" * bp."Rent"
  END AS "Rent_due",
  'Pending' AS "Rent_status", NULL AS "Payment_method", NULL AS "Payment_date", NULL as "Invoice"
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b on b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id" 
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id"
WHERE bp."Invoice_rent_id" IS NULL 
  AND bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
)
ORDER BY "Owner", "Month", "Year", "Code"

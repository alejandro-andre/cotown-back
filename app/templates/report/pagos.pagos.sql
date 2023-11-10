(
SELECT pr."Name" as "Owner", bp."Booking_id",
  EXTRACT(MONTH from bp."Rent_date") AS "Month", EXTRACT(YEAR from bp."Rent_date") AS "Year",
  r."Code", c."Name", b."Date_from", b."Date_to",
  bp."Rent" + COALESCE(bp."Rent_discount", 0) as "Rent",
  CASE WHEN p."Payment_date" IS NULL THEN bp."Rent" + COALESCE(bp."Rent_discount", 0) ELSE 0.0 END AS "Rent_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Rent_status",
  b."Deposit_actual" AS "Deposit",
  pm."Name" AS "Payment_method", p."Payment_date" 
FROM "Booking"."Booking_price" bp 
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id" 
  LEFT JOIN "Billing"."Invoice" i on i.id = bp."Invoice_rent_id"
  LEFT JOIN "Billing"."Payment" p on p.id = i."Payment_id"
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE bp."Rent_date" >= %(fdesde)s AND bp."Rent_date" < %(fhasta)s
  AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
)
UNION 
(
SELECT DISTINCT ON (b.id)
  pr."Name" as "Owner", bp."Booking_id",
  EXTRACT(MONTH from bp."Rent_date") AS "Month", EXTRACT(YEAR from bp."Rent_date") AS "Year",
  CONCAT(bu."Code", ' (', b."Rooms", ') plazas'), c."Name", b."Date_from", b."Date_to",
  b."Rooms" * bp."Rent" as "Rent",
  CASE WHEN p."Payment_date" IS NULL THEN b."Rooms" * bp."Rent" ELSE 0.0 END AS "Rent_due",
  CASE WHEN p."Payment_date" IS NULL THEN 'Pending' ELSE 'Paid' END AS "Rent_status",
  b."Rooms" * b."Deposit",
  pm."Name" AS "Payment_method", p."Payment_date" 
FROM "Booking"."Booking_group_price" bp 
  INNER JOIN "Booking"."Booking_group" b on b.id = bp."Booking_id" 
  INNER JOIN "Booking"."Booking_rooming" br on b.id = br."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"  
  INNER JOIN "Provider"."Provider" pr on pr.id = r."Owner_id"  
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"  
  INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id" 
  LEFT JOIN "Billing"."Invoice" i on i.id = bp."Invoice_rent_id"
  LEFT JOIN "Billing"."Payment" p on p.id = i."Payment_id"
  LEFT JOIN "Billing"."Payment_method" pm on pm.id = p."Payment_method_id"
WHERE bp."Rent_date" BETWEEN %(fdesde)s AND %(fhasta)s
  AND r."Owner_id" BETWEEN %(pdesde)s AND %(phasta)s
)
ORDER BY 1, 4
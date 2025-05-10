SELECT 
  b.id AS "Booking_id",
  b."Date_from", b."Date_to",
  b."Deposit_required", b."Date_deposit_required", b."Deposit_returned", b."Date_deposit_returned",
  c."Name" AS "Customer",
  r."Code" AS "Resource",
  bu."Code" AS "Building"
FROM "Booking"."Booking" b 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
WHERE b."Status" = 'devolvergarantia' 
  AND (b."Date_deposit_required" BETWEEN '{date_from}' AND '{date_to}' OR b."Date_deposit_required" IS NULL)

SELECT 
  b.id, 
  b."Status", 
  c."Name", 
  b."Date_from", 
  b."Date_to", 
  b."Check_in", 
  bu."Name" AS "Building", 
  r."Code" AS "Resource", 
  b."Issues",
  b."Damages",
  b."Flight", 
  b."Arrival", 
  b."Check_in_time", 
  ct."Name" AS "Option"
FROM "Booking"."Booking" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id"
  LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Booking"."Checkin_type" ct ON ct.id = b."Check_in_option_id"
WHERE COALESCE("Check_in", "Date_from") BETWEEN CURRENT_DATE + INTERVAL '1 days' AND CURRENT_DATE + INTERVAL '14 days'
  AND b."Status" IN ('firmacontrato', 'contrato', 'checkinconfirmado')

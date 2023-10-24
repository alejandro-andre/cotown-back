SELECT b.id, b."Status", c."Name", b."Date_from", b."Date_to", b."Check_in", r."Code" as "Resource", b."Flight", b."Arrival", ct."Name" AS "Option"
FROM "Booking"."Booking" b 
INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id" 
LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
LEFT JOIN "Booking"."Checkin_type" ct ON ct.id = b."Check_in_option_id"
WHERE GREATEST("Check_in", "Date_from") BETWEEN CURRENT_DATE + INTERVAL '1 days' AND CURRENT_DATE + INTERVAL '14 days'

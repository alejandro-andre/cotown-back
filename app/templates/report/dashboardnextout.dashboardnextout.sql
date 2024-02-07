SELECT b.id, b."Status", c."Name", b."Date_from", b."Date_to", b."Check_out", bu."Name" as "Building", r."Code" as "Resource"
FROM "Booking"."Booking" b
INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id"
LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
LEFT JOIN "Booking"."Checkin_type" ct ON ct.id = b."Check_in_option_id"
WHERE COALESCE("Check_out", "Date_to") BETWEEN CURRENT_DATE + INTERVAL '1 days' AND CURRENT_DATE + INTERVAL '30 days'
AND b."Status" IN ('inhouse')

SELECT 
  b.id::text || '-' || ab.id::text as "id",
  b.id AS "booking",
  a."Name" AS "marketplace",
  ab."Amount" AS "amount",
  ab."Date_from" AS "date_from", 
  ab."Date_to" AS "date_to",
  COUNT(b.id) OVER (PARTITION BY ab.id) AS "count",
  CASE 
    WHEN COUNT(b.id) OVER (PARTITION BY ab.id) > 0 THEN 
      ab."Amount" / COUNT(b.id) OVER (PARTITION BY ab.id)
    ELSE 0
  END AS "cost"
FROM "Provider"."Agent_bills" ab
  INNER JOIN "Provider"."Agent" a ON a.id = ab."Agent_id"
  LEFT JOIN "Booking"."Booking" b 
    ON b."Agent_id" = ab."Agent_id" 
   AND ab."Date_from" <= b."Confirmation_date" 
   AND ab."Date_to" >= b."Confirmation_date"
WHERE b.id IS NOT NULL
ORDER BY 1
;
SELECT 
  r."Code",
  substring(r."Registry_num", 11, 14) AS "CRU", 
  r."Registry_num" AS "NRUA",
  CASE 
  	WHEN Count(b.*) > 0 THEN 'Si'
  	ELSE 'No'
  END AS "Bookings"
FROM "Resource"."Resource" r  
  LEFT JOIN "Booking"."Booking" b ON r.id = b."Resource_id"
WHERE b."Status" IS NULL 
  OR(
    b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
    AND EXTRACT(YEAR FROM b."Date_from") <= %(year)s 
  	AND EXTRACT(YEAR FROM b."Date_to") >= %(year)s
  )
GROUP BY 1, 2, 3
ORDER BY 1
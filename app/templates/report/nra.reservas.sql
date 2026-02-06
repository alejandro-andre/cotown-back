SELECT 
  b.id,
  r."Code",
  substring(r."Registry_num", 11, 14) AS "CRU", 
  r."Registry_num" AS "NRUA",
  CASE 
	WHEN b."Reason_id" IN (5) THEN 1    -- Vacacional
	WHEN b."Reason_id" IN (2, 4) THEN 2 -- Laboral
	WHEN b."Reason_id" IN (1, 3) THEN 3 -- Estudios
  	ELSE NULL
  END AS "Reason", 
  1 AS "Pax",
  b."Date_from",
  b."Date_to"
FROM "Booking"."Booking" b 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Booking"."Customer_reason" cr ON cr.id = b."Reason_id" 
WHERE b."Status" NOT IN ('cancelada')
  AND EXTRACT(YEAR FROM b."Date_from") <= %(year)s
  AND EXTRACT(YEAR FROM b."Date_to") >= %(year)s
ORDER BY 3, 2, 1

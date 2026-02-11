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
  GREATEST(b."Date_from"::date, make_date(%(year)s, 1, 1)) AS "Date_from",
  LEAST(b."Date_to"::date, make_date(%(year)s, 12, 31)) AS "Date_to"
FROM "Booking"."Booking" b 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Booking"."Customer_reason" cr ON cr.id = b."Reason_id" 
WHERE b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
  AND b."Date_from"::date <= make_date(%(year)s, 12, 31)
  AND b."Date_to"::date   >= make_date(%(year)s, 1, 1)
ORDER BY 3, 2, 1

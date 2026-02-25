SELECT
  b.id,
  r."Code",
  substring(r."Registry_num", 11, 14) AS "CRU", 
  r."Registry_num" AS "NRUA",
  CASE 
    WHEN b."id" IS NULL THEN NULL
    WHEN b."Reason_id" IN (5)    THEN 1 -- Vacacional
    WHEN b."Reason_id" IN (2, 4) THEN 2 -- Laboral
    WHEN b."Reason_id" IN (1, 3) THEN 3 -- Estudios
    ELSE NULL
  END AS "Reason", 
  CASE 
    WHEN b."id" IS NULL THEN NULL
    ELSE 1
  END AS "Pax",
  CASE 
    WHEN b."id" IS NULL THEN NULL
    ELSE GREATEST(b."Date_from"::date, make_date(%(year)s, 1, 1))
  END AS "Date_from",
  CASE 
    WHEN b."id" IS NULL THEN NULL
    ELSE LEAST(b."Date_to"::date, make_date(%(year)s, 12, 31)) 
  END AS "Date_to",
  a."Name" as "Marketplace"
FROM "Resource"."Resource" r 
  LEFT JOIN "Booking"."Booking" b ON r."id" = b."Resource_id"
    AND (
      b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
      AND b."Date_from"::date <= make_date(%(year)s, 12, 31)
      AND b."Date_to"::date   >= make_date(%(year)s, 1, 1)
    )
  LEFT JOIN "Booking"."Customer_reason" cr ON cr."id" = b."Reason_id"
  LEFT JOIN "Provider"."Agent" a ON a."id" = b."Agent_id"
ORDER BY 3, 2, 1
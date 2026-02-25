SELECT 
  r."Code",
  substring(r."Registry_num", 11, 14) AS "CRU", 
  r."Registry_num" AS "NRUA",
  CASE 
    WHEN Count(b.*) > 0 THEN 'Si'
    ELSE 'No'
  END AS "Bookings"
FROM "Resource"."Resource" r  
  LEFT JOIN "Booking"."Booking" b ON r."id" = b."Resource_id"
    AND (
      b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
      AND b."Date_from"::date <= make_date(%(year)s, 12, 31)
      AND b."Date_to"::date   >= make_date(%(year)s, 1, 1)
    )
GROUP BY 1, 2, 3
ORDER BY 1
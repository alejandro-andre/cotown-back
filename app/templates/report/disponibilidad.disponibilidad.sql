WITH
"Dates" AS (
  SELECT generate_series(%(fdesde)s::date, %(fhasta)s::date - interval '1 day', interval '1 day') AS "Date"
),
"Bookings" AS (
  SELECT 
    r.id,
    d."Date",
    CASE
      WHEN b."Availability_id" IS NOT NULL THEN 'No disponible'
      WHEN b."Lock" THEN 'Bloqueado'
      WHEN NOT b."Lock" THEN 'Reservado'
      ELSE 'Disponible'
    END AS "Availability",
    CASE
      WHEN b."Status" IS NULL THEN 'Disponible'
      WHEN b."Availability_id" IS NOT NULL THEN b."Status"
      WHEN b."Booking_id" IS NOT NULL THEN etlb.labels[array_position(etb.values, b."Status")]
      ELSE etlg.labels[array_position(etg.values, b."Status")]
    END AS "Status"
  FROM 
    "Resource"."Resource" r
    CROSS JOIN "Dates" d
    LEFT JOIN "Booking"."Booking_detail" b ON r."id" = b."Resource_id" AND d."Date" BETWEEN b."Date_from" AND b."Date_to"
    INNER JOIN "Models"."EnumType" etb ON etb.id = 7
    INNER JOIN "Models"."EnumType" etg ON etg.id = 13
    INNER JOIN "Models"."EnumTypeLabel" etlb ON etlb.container = etb.id AND etlb.locale = 'es_ES'
    INNER JOIN "Models"."EnumTypeLabel" etlg ON etlg.container = etg.id AND etlg.locale = 'es_ES'
),
"Changes" AS (
  SELECT 
    b.id,
    b."Date",
    b."Availability",
    b."Status",
    LAG(b."Status") OVER (PARTITION BY b.id ORDER BY "Date") <> b."Status" OR  
    LAG(b."Status") OVER (PARTITION BY b.id ORDER BY "Date") IS NULL AS "Change"
  FROM 
    "Bookings" b
),
"Ranges" AS (
  SELECT 
    c.id,
    c."Date",
    c."Availability",    
    c."Status",    
    SUM(CASE WHEN c."Change" THEN 1 ELSE 0 END) OVER (PARTITION BY c.id ORDER BY c."Date") AS "Group"
  FROM "Changes" c
),
"Aggregate" AS (
  SELECT 
    r.id,
    r."Availability",
    r."Status",
    TO_CHAR(MIN(r."Date"), 'YYYY-MM-DD') AS "From",
    TO_CHAR(MAX(r."Date"), 'YYYY-MM-DD') AS "To"
  FROM 
    "Ranges" r
  GROUP BY 1, 2, 3
)
SELECT 
  SUBSTRING(r."Code", 1, 6) AS "Building",
  r."Code" AS "Resource",
  rft."Code" AS "Flat_type",
  rpt."Code" AS "Place_type",
  a."Availability",
  a."Status",
  a."From",
  a."To"
FROM "Aggregate" a 
  INNER JOIN "Resource"."Resource" r ON r.id = a.id
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
WHERE b."Active"
ORDER BY 2
;
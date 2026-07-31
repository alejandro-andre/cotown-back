-- Contratos B2C (reservas individuales)
SELECT
  b.id::text                      AS "Id",
  r."Code"                        AS "Resource",
  COALESCE(etlb.labels[array_position(etb.values, b."Status"::text)], b."Status"::text) AS "Status",
  c.id                            AS "Customer_id",
  c."Name"                        AS "Customer_name",
  c."Email"                       AS "Customer_email",
  b."Date_from"                   AS "Date_from",
  b."Date_to"                     AS "Date_to",
  (b."Contract_rent").name        AS "Contract_rent",
  (b."Contract_services").name    AS "Contract_services",
  b."Contract_status"::text       AS "Contract_status",
  b."Contract_signed"             AS "Contract_signed",
  b."Contract_id"                 AS "Contract_id",
  b.id                            AS "Sort_id"
FROM "Booking"."Booking" b
  LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Models"."EnumType" etb ON etb.id = 7
  INNER JOIN "Models"."EnumTypeLabel" etlb ON etlb.container = etb.id AND etlb.locale = 'es_ES'
WHERE b."Date_from" <= %(fhasta)s AND b."Date_to" >= %(fdesde)s
  AND ((b."Contract_rent").name IS NOT NULL OR (b."Contract_services").name IS NOT NULL)

UNION ALL

-- Contratos B2B (reservas de grupo)
SELECT
  'B' || g.id,
  bu."Code" || ' (' || g."Rooms" || ' plazas)',
  COALESCE(etlg.labels[array_position(etg.values, g."Status"::text)], g."Status"::text),
  c.id,
  c."Name",
  c."Email",
  g."Date_from",
  g."Date_to",
  (g."Contract_rent").name,
  (g."Contract_services").name,
  g."Contract_status"::text,
  g."Contract_signed",
  g."Contract_id",
  1000000 + g.id AS "Sort_id"
FROM "Booking"."Booking_group" g
  LEFT JOIN "Building"."Building" bu ON bu.id = g."Building_id"
  LEFT JOIN "Customer"."Customer" c ON c.id = g."Payer_id"
  INNER JOIN "Models"."EnumType" etg ON etg.id = 13
  INNER JOIN "Models"."EnumTypeLabel" etlg ON etlg.container = etg.id AND etlg.locale = 'es_ES'
WHERE g."Date_from" <= %(fhasta)s AND g."Date_to" >= %(fdesde)s
  AND ((g."Contract_rent").name IS NOT NULL OR (g."Contract_services").name IS NOT NULL)

-- Primero las B2C, luego las B2B (+1000000), cada bloque por nº de reserva
ORDER BY "Sort_id"
;

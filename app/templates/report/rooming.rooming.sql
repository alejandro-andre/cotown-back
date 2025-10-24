SELECT
  bgr.id,
  bgr."Booking_id",
  bgp."Code" AS "Resource.Code",
  bgr."Check_in",
  bgr."Check_out",
  bgr."Document",
  bgr."Name",
  bgr."Email",
  bgr."Phones",
  bgr."Address",
  bgr."Zip",
  bgr."City",
  bgr."Province",
  i."Name" AS "Id_type.Name",
  c."Name" AS "Country.Name",
  g."Name" AS "Gender.Name",
  l."Name" AS "Language.Name",
  n."Name" AS "Nationality.Name",
  o."Name" AS "Origin.Name"
FROM "Booking"."Booking_group_rooming" bgr
  LEFT JOIN "Booking"."Booking_group_rooms" bgp ON bgr."Booking_id" = bgp."Booking_id" AND bgr."Room_id" = bgp.id
  LEFT JOIN "Auxiliar"."Id_type" i ON i.id = bgr."Id_type_id" 
  LEFT JOIN "Auxiliar"."Gender" g ON g.id = bgr."Gender_id" 
  LEFT JOIN "Auxiliar"."Language" l ON l.id = bgr."Language_id" 
  LEFT JOIN "Geo"."Country" c ON c.id = bgr."Country_id" 
  LEFT JOIN "Geo"."Country" o ON o.id = bgr."Country_origin_id" 
  LEFT JOIN "Geo"."Country" n ON n.id = bgr."Nationality_id"
WHERE bgr."Booking_id" = %(id)s
UNION ALL
SELECT 
  NULL::int AS id,
  %(id)s::int AS "Booking_id",
  NULL::text AS "Resource.Code",
  NULL::date AS "Check_in",
  NULL::date AS "Check_out",
  NULL::text AS "Document",
  NULL::text AS "Name",
  NULL::text AS "Email",
  NULL::text AS "Phones",
  NULL::text AS "Address",
  NULL::text AS "Zip",
  NULL::text AS "City",
  NULL::text AS "Province",
  NULL::text AS "Id_type.Name",
  NULL::text AS "Country.Name",
  NULL::text AS "Gender.Name",
  NULL::text AS "Language.Name",
  NULL::text AS "Nationality.Name",
  NULL::text AS "Origin.Name"
FROM generate_series(1, 40)
ORDER BY 4, 3;
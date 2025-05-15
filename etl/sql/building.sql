SELECT
  b."Code" AS id,
  b."Name" AS "name",
  b."Address" AS "address",
  b."Lat_lon"[0] AS "lat",
  b."Lat_lon"[1] AS "lon",
  b."Start_date" AS "start_date",
  l."Name" AS "city"
FROM "Building"."Building" b
  INNER JOIN "Geo"."District" d ON d.id = b."District_id"
  INNER JOIN "Geo"."Location" l ON l.id = d."Location_id";
SELECT
  "Code" AS id,
  "Name" AS "name",
  "Address" AS "address",
  "Lat_lon"[0] AS "lat",
  "Lat_lon"[1] AS "lon"
FROM
  "Building"."Building";
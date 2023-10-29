set myapp.admin='false';
update "Billing"."Invoice" set "Issued" = false, "Code" = NULL;
delete from "Billing"."Invoice_line";
delete from "Billing"."Invoice";
;
-- ---------------------------------------------
-- Reset migración
-- ---------------------------------------------

-- Borrar auxiliares
TRUNCATE TABLE "Batch"."Upload" RESTART IDENTITY CASCADE;

-- Borrar pagos y facturas
SET myapp.admin='false';
UPDATE "Billing"."Invoice" SET "Issued" = FALSE, "Code" = NULL;
DELETE FROM "Billing"."Invoice_line";
DELETE FROM "Billing"."Invoice";
TRUNCATE TABLE "Provider"."Provider_bill" RESTART IDENTITY;
TRUNCATE TABLE "Billing"."Payment" RESTART IDENTITY;

-- Borrar reservas
TRUNCATE TABLE "Booking"."Booking" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_option" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_price" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_detail" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_log" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Booking"."Booking_group" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_group_price" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_rooming" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Booking"."Booking_detail" RESTART IDENTITY CASCADE;
--SELECT setval('"Booking"."Booking_id_seq"', 10000, false);

-- Borrar clientes
DELETE FROM "Models"."User" WHERE username LIKE 'C%';
TRUNCATE TABLE "Customer"."Customer" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Customer"."Customer_contact" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Customer"."Customer_email" RESTART IDENTITY CASCADE;
--TRUNCATE TABLE "Customer"."Customer_doc" RESTART IDENTITY CASCADE;

-- ---------------------------------------------
-- Check post migración
-- ---------------------------------------------

-- Post clientes
SELECT count(*) FROM "Customer"."Customer";
SELECT max(id) FROM "Customer"."Customer";
SELECT count(*) FROM "Customer"."Customer_email";

-- Post bookings
TRUNCATE TABLE "Booking"."Booking_price" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Booking"."Booking_group_price" RESTART IDENTITY CASCADE;
SELECT count(*) FROM "Booking"."Booking";

-- Post precios
SELECT count(*) FROM "Booking"."Booking_price";

SELECT b.id, b."Status", c."Name", c."Email", count(bp.id)
FROM "Booking"."Booking" b
INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id"
LEFT JOIN "Booking"."Booking_price" bp ON b.id = bp."Booking_id"
GROUP BY 1, 2, 3, 4
ORDER BY 5 ASC;

UPDATE "Booking"."Booking" set id = id;
UPDATE "Booking"."Booking_group" set id = id;

SELECT count(*) FROM "Booking"."Booking_price";
SELECT count(*) FROM "Booking"."Booking_group_price";
SELECT count(*) FROM "Billing"."Invoice";
SELECT count(*) FROM "Billing"."Payment";

-- ---------------------------------------------
-- Dynamic web queries
-- ---------------------------------------------

-- Habitaciones
SELECT DISTINCT b.id, b."Code" as "Building_code",
       rpt."Code" AS "Place_type_code",
       rft."Code" AS "Flat_type_code",
       b."Name" as "Building_name",
       rpt."Name" AS "Place_type_name",
       rft."Name" AS "Flat_type_name",
       pd."Rent_long" AS "Price",
       mrt.id
FROM "Resource"."Resource" r
     INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
     INNER JOIN "Geo"."District" d ON d.id = b."District_id"
     INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
     INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
     INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Year" = 2024 AND pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
     INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Place_type_id" = rpt.id)
     LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2024-03-31' AND bd."Date_to" >= '2023-11-01')
WHERE bd.id IS NULL
  AND b."Segment_id" = 1
  AND b."Building_type_id" < 3
  AND d."Location_id" = 1
  AND rpt."Code" LIKE 'I\_%';

-- ---------------------------------------------
-- SAP API
-- ---------------------------------------------

SELECT DISTINCT "Type", "case" AS "Third_party", "Document", "Name", "Address", "Zip", "City", "Province", "Code" AS "Country", "Email"
FROM (
  SELECT c."Type", CASE WHEN r."Owner_id" = 10 THEN 'true' ELSE 'false' END CASE, c."Document", c."Name", c."Address", c."Zip", c."City", c."Province", co."Code" , c."Email"
  FROM "Booking"."Booking_price" bp
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id"
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"
  INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id"
  INNER JOIN "Geo"."Country" co on co.id = c."Country_id"
  WHERE (c."Created_at" > '2023-01-01' OR c."Updated_at" > '2023-01-01')
  UNION
  SELECT c."Type", CASE WHEN r."Owner_id" = 10 THEN 'true' ELSE 'false' END CASE, c."Document", c."Name", c."Address", c."Zip", c."City", c."Province", co."Code" , c."Email"
  FROM "Booking"."Booking_rooming" br
  INNER JOIN "Booking"."Booking_group" bg on bg.id = br."Booking_id"
  INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id"
  INNER JOIN "Customer"."Customer" c on c.id = bg."Payer_id"
  INNER JOIN "Geo"."Country" co on co.id = c."Country_id"
  WHERE (c."Created_at" > '2023-01-01' OR c."Updated_at" > '2023-01-01')
) AS customers
ORDER BY 3;


-- ---------------------------------------------
-- Utilidades
-- ---------------------------------------------

-- Habitaciones y pisos disponibles entre dos fechas
SELECT
  b."Name", r."Flat_type_id", r."Place_type_id",
  ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0) AS "Rent_long",
  ROUND(pd."Services" + pr."Multiplier" * pd."Rent_medium", 0) AS "Rent_medium",
  ROUND(pd."Services" + pr."Multiplier" * pd."Rent_short", 0) AS "Rent_short",
  COUNT(*) AS "Qty"
FROM
  "Resource"."Resource" r
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  INNER JOIN "Geo"."District" d on d.id = b."District_id"
  INNER JOIN "Resource"."Resource_flat_type" rft ON r."Flat_type_id" = rft.id
  INNER JOIN "Resource"."Resource_place_type" rpt ON r."Place_type_id" = rpt.id
  INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
  INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id"
    AND pd."Flat_type_id" = r."Flat_type_id"
    AND (pd."Place_type_id" = r."Place_type_id" OR pd."Place_type_id" IS NULL)
  LEFT JOIN "Booking"."Booking_detail" bd ON bd."Resource_id" = r.id
    AND bd."Date_from" <= '2023-12-31'
    AND bd."Date_to" >= '2023-10-01'
WHERE b."Active"
  AND pd."Year" = 2023
  AND d."Location_id" = 1
  AND bd.id IS NULL
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY 1, 2, 3;

-- Tipologías de habitaciones en piso compartido
SELECT
  r."Building_id", rpt."Code" AS "Place_type", rft."Code" AS "Flat_type",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0)) AS "Rent_long",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_medium", 0)) AS "Rent_medium",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_short", 0)) AS "Rent_short",
  COUNT(*) AS "Qty"
FROM
  "Resource"."Resource" r
  INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
  INNER JOIN "Resource"."Resource_flat_type" rft ON r."Flat_type_id" = rft.id
  INNER JOIN "Resource"."Resource_place_type" rpt ON r."Place_type_id" = rpt.id
  INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
  INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" = r."Place_type_id"
WHERE pd."Year" = 2023
  AND rpt.id < 300
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
   
-- Tipologías de apartamentos privados
SELECT
  r."Building_id", rfst."Code" AS "Flat_subtype",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0)) AS "Rent_long",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_medium", 0)) AS "Rent_medium",
  MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_short", 0)) AS "Rent_short",
  COUNT(*) AS "Qty"
FROM
  "Resource"."Resource" r
  INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
  INNER JOIN "Resource"."Resource_flat_subtype" rfst ON r."Flat_subtype_id" = rfst.id
  INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
  INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" IS NULL
WHERE pd."Year" = 2023
GROUP BY 1, 2
ORDER BY 1, 2;
  
-- Borrar imagenes
DELETE FROM pg_largeobject CASCADE;
VACUUM FULL;
VACUUM ANALYZE;

-- Modificacion secuencia
ALTER SEQUENCE "Resource"."Resource_id_seq" RESTART WITH 1;

-- Borrar tablas
TRUNCATE TABLE "Customer"."Customer_contact" CASCADE;
TRUNCATE TABLE "Customer"."Customer" CASCADE;
TRUNCATE TABLE "Customer"."Customer_email" CASCADE;
TRUNCATE TABLE "Booking"."Booking" CASCADE;
TRUNCATE TABLE "Booking"."Booking_price" CASCADE;
TRUNCATE TABLE "Booking"."Booking_group" CASCADE;
TRUNCATE TABLE "Booking"."Booking_detail" CASCADE;
TRUNCATE TABLE "Booking"."Booking_log" CASCADE;
TRUNCATE TABLE "Billing"."Invoice" CASCADE;
TRUNCATE TABLE "Billing"."Payment" CASCADE;
TRUNCATE TABLE "Resource"."Resource" CASCADE;

-- Update
UPDATE "Booking"."Booking" SET id=id;
UPDATE "Booking"."Booking_rooming" SET id=id;
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'piso';
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'habitacion';
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'plaza';
UPDATE "Resource"."Resource_availability" SET id=id;
UPDATE "Billing"."Payment" SET id=id;
UPDATE "Billing"."Invoice" SET "Rectified"=FALSE;
UPDATE "Provider"."Provider" SET id=id;
UPDATE "Customer"."Customer" SET "User_name" = NULL WHERE id=916;
UPDATE "Customer"."Customer_email" SET "Sent_at" = NULL, "Body" = NULL, "Subject" = NULL;
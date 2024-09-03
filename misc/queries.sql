-- ---------------------------------------------
-- Availability by building and types
-- ---------------------------------------------

SELECT 
  r."Building_id", SUBSTRING(COALESCE(rpt."Code", 'F'), 1, 1), COUNT(*)
FROM
  "Resource"."Resource" r
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
  LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2024-01-31' AND bd."Date_to" >= '2023-12-01')
WHERE (rpt."Code" IS NULL OR rpt."Code" NOT LIKE 'DUI%')
  AND bd.id IS NULL
GROUP BY 1, 2
ORDER BY 1, 2
;

SELECT 
  r."Building_id", rpt."Code", rft."Code", COUNT(*)
FROM
  "Resource"."Resource" r
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
  LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2024-01-31' AND bd."Date_to" >= '2023-12-01')
WHERE rpt."Code" NOT LIKE 'DUI%'
  AND bd.id IS NULL
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3
;

SELECT 
  r."Building_id", rfst."Code", rft."Code", COUNT(*)
FROM
  "Resource"."Resource" r
  INNER JOIN "Resource"."Resource_flat_subtype" rfst ON rfst.id = r."Flat_subtype_id"
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
  LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2025-01-31' AND bd."Date_to" >= '2024-12-01')
WHERE bd.id IS NULL
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3
;

-- ---------------------------------------------
-- Bills and future income
-- ---------------------------------------------

SELECT "Name", "Date", SUM("Rent"), SUM("Services")
FROM (
SELECT bu."Name", bu."Code", i."Code", DATE_TRUNC('month', i."Issued_date") AS "Date", 
  CASE WHEN p."Product_type_id" = 3 THEN il."Amount" ELSE 0 END AS "Rent",
  CASE WHEN p."Product_type_id" <> 3 THEN il."Amount" ELSE 0 END AS "Services"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Product" p on p.id = il."Product_id" 
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id" 
  INNER JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
  INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"  
WHERE i."Issued" AND p."Product_type_id" > 2
UNION ALL
SELECT bu."Name", r."Code", i."Code", DATE_TRUNC('month', i."Issued_date") AS "Date", 
  CASE WHEN p."Product_type_id" = 3 THEN il."Amount" ELSE 0 END AS "Rent",
  CASE WHEN p."Product_type_id" <> 3 THEN il."Amount" ELSE 0 END AS "Services"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Product" p on p.id = il."Product_id" 
  INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id" 
  INNER JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"  
WHERE i."Issued" AND i."Issued" AND p."Product_type_id" > 2
UNION ALL
SELECT 
  bu."Name" AS "Building", (bu."Code" || '-' || b.id) AS "Resource", '', DATE_TRUNC('month', bp."Rent_date") AS "Date", 
  b."Rooms" * b."Rent" AS "Rent",
  b."Rooms" * b."Services" AS "Services"
FROM "Booking"."Booking_group" b
INNER JOIN "Booking"."Booking_group_price" bp ON bp."Booking_id" = b.id
INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"
WHERE bp."Invoice_rent_id" IS NULL AND "Rent_date" > '2023-11-01'
UNION ALL
SELECT 
  bu."Name" AS "Building", r."Code" AS "Resource", '', DATE_TRUNC('month', bp."Rent_date") AS "Date",
  bp."Rent" + COALESCE(bp."Rent_discount", 0) AS "Rent",
  bp."Services" + COALESCE(bp."Services_discount", 0) AS "Services"
FROM "Booking"."Booking_price" bp
INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id"
INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
WHERE bp."Invoice_rent_id" IS NULL AND "Rent_date" > '2023-11-01'
) AS income
GROUP BY 1, 2
ORDER BY 1, 2
;
    
-- ---------------------------------------------
-- Check locks
-- ---------------------------------------------

select b."Date_from", b."Date_to" 
from "Booking"."Booking" b 
where b.id = 1628
;

select b."Booking_id"  
from "Booking"."Booking_detail" b 
where b."Resource_id" = 265
and b."Booking_id" <> 1628
and b."Date_from" <= '2024-02-11' 
and b."Date_to" >= '2023-09-01'
limit 1
;

-- ---------------------------------------------
-- Bugs
-- ---------------------------------------------

--SET myapp.admin='true';

-- ---------------------------------------------
-- SAP
-- ---------------------------------------------

  SELECT DISTINCT * FROM (
    SELECT
      c.id,
      c."Type" AS "type", 
      CASE 
        WHEN r."Owner_id" = 10 THEN FALSE
        ELSE TRUE
      END AS "third_party",
      i."Name" AS "document_type",
      CASE 
        WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES'
        ELSE na."Code" 
      END AS "document_country",
      c."Document" AS "document", 
      c."Name" AS "name", 
      c."Address" AS "address", 
      c."Zip" AS "zip", 
      c."City" AS "city", 
      COALESCE(c."Province", '') AS "province", 
      co."Code" AS "country",
      COALESCE(c."Bank_account", '') AS "bank_account"
    FROM "Customer"."Customer" c
      INNER JOIN "Booking"."Booking_group" b ON b."Payer_id" = c.id
      INNER JOIN "Booking"."Booking_group_rooming" br ON br."Booking_id" = b.id
      LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
      LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
      LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
      LEFT JOIN "Resource"."Resource" r ON r.id = br."Resource_id" 
    --WHERE 
      --c."Created_at" >= '{date}' OR 
      --c."Updated_at" >= '{date}' OR
      --b."Created_at" >= '{date}' OR 
      --b."Updated_at" >= '{date}'
    UNION ALL
    SELECT
      c.id,
      c."Type" AS "type", 
      CASE 
        WHEN r."Owner_id" = 10 THEN FALSE
        ELSE TRUE
      END AS "third_party",
      i."Name" AS "document_type",
      CASE 
        WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES'
        ELSE na."Code" 
      END AS "document_country",
      c."Document" AS "document", 
      c."Name" AS "name", 
      c."Address" AS "address", 
      c."Zip" AS "zip", 
      c."City" AS "city", 
      COALESCE(c."Province", '') AS "province", 
      co."Code" AS "country",
      COALESCE(c."Bank_account", '') AS "bank_account"
    FROM "Customer"."Customer" c
      INNER JOIN "Booking"."Booking" b ON b."Customer_id" = c.id
      LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
      LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
      LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
      LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
    WHERE 
      b."Status" NOT IN ('solicitud', 'alternativas', 'pendientepago', 'finalizada', 'descartada', 'cancelada', 'caducada')
      --c."Created_at" >= '{date}' OR 
      --c."Updated_at" >= '{date}' OR
      --b."Created_at" >= '{date}' OR 
      --b."Updated_at" >= '{date}'
  ) AS customers
ORDER BY 1
;

-- ---------------------------------------------
-- Reset migracion
-- ---------------------------------------------

VACUUM FULL;
SELECT pg_size_pretty(pg_database_size('niledb'));

-- Borrar auxiliares
TRUNCATE TABLE "Batch"."Upload" RESTART IDENTITY;

-- Borrar pagos y facturas
TRUNCATE TABLE "Provider"."Provider_bill" RESTART IDENTITY;
TRUNCATE TABLE "Billing"."Payment" RESTART IDENTITY CASCADE;

-- Borrar reservas
TRUNCATE TABLE "Booking"."Booking" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Booking"."Booking_group" RESTART IDENTITY CASCADE;

-- Borrar clientes
SELECT COUNT(*) FROM "Models"."User" WHERE username LIKE 'C%';
DELETE FROM "Models"."User" WHERE username LIKE 'C%';
TRUNCATE TABLE "Customer"."Customer" RESTART IDENTITY;

-- ---------------------------------------------
-- Post carga clientes
-- ---------------------------------------------

SELECT COUNT(*) FROM "Customer"."Customer";
SELECT MAX(id) FROM "Customer"."Customer";
SELECT COUNT(*) FROM "Customer"."Customer_email";
DELETE FROM "Customer"."Customer_email";
TRUNCATE TABLE "Booking"."Booking" RESTART IDENTITY CASCADE;
TRUNCATE TABLE "Booking"."Booking_group" RESTART IDENTITY CASCADE;

-- ---------------------------------------------
-- Post bookings
-- ---------------------------------------------

SELECT COUNT(*) FROM "Booking"."Booking";
SELECT COUNT(*) FROM "Booking"."Booking_group";
SELECT COUNT(*) FROM "Booking"."Booking_group_rooming";
SELECT SUM("Rooms") FROM "Booking"."Booking_group";
SELECT "Booking_id", COUNT(*) FROM "Booking"."Booking_group_rooming" GROUP BY 1 ORDER BY 1;

-- ---------------------------------------------
-- Post precios
-- ---------------------------------------------

SELECT COUNT(*) FROM "Booking"."Booking_price";
SELECT COUNT(*) FROM "Booking"."Booking_group_price";
UPDATE "Booking"."Booking_price" SET "Updated_by" = 'migration';
UPDATE "Booking"."Booking_group_price" SET "Updated_by" = 'migration';
SELECT b.id, b."Status", r."Code", b."Date_from", b."Date_to", c."Name", c."Email", count(bp.id)
FROM "Booking"."Booking" b
INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"
INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id" 
LEFT JOIN "Booking"."Booking_price" bp ON b.id = bp."Booking_id" 
GROUP BY 1, 2, 3, 4, 5, 6, 7
ORDER BY 8 ASC;

-- ---------------------------------------------
-- Post grupos
-- ---------------------------------------------

UPDATE "Booking"."Booking_group" SET "Status" = 'grupobloqueado' WHERE "Status" = 'inhouse';
UPDATE "Booking"."Booking_group" SET "Status" = 'inhouse' WHERE "Status" = 'grupobloqueado';
UPDATE "Booking"."Booking_group" SET "Status" = 'grupobloqueado' WHERE "Status" = 'grupoconfirmado';
UPDATE "Booking"."Booking_group" SET "Status" = 'grupoconfirmado' WHERE "Status" = 'grupobloqueado';
SELECT COUNT(*) FROM "Booking"."Booking_group_price";

-- ---------------------------------------------
-- Usuarios
-- ---------------------------------------------

SELECT COUNT(*) FROM (
  SELECT c."User_name", COUNT(*) 
  FROM "Customer"."Customer" c
  INNER JOIN "Booking"."Booking" b on b."Customer_id" = c.id 
  WHERE b."Status" NOT IN ('finalizada')
  GROUP BY 1
) AS C;

UPDATE "Customer"."Customer_email" SET "Sent_at" = NULL;

SELECT COUNT(*) FROM "Customer"."Customer" c WHERE "User_name" LIKE 'C%'

UPDATE "Customer"."Customer" c
SET "User_name" = NULL
FROM "Booking"."Booking" b
WHERE b."Customer_id" = c."id" AND b."Status" NOT IN ('finalizada');

-- ---------------------------------------------
-- Actualizar reservas
-- ---------------------------------------------

UPDATE "Booking"."Booking" b SET "Status" = 'inhouse' WHERE "Date_from" < '2023-11-02' AND "Status" = 'confirmada';
UPDATE "Booking"."Booking" b SET "Status" = 'firmacontrato' WHERE "Status" = 'confirmada';
UPDATE "Booking"."Booking" set id = id;
UPDATE "Booking"."Booking_group" set id = id;
UPDATE "Resource"."Resource_availability" set id = id;

-- ---------------------------------------------
-- Emails
-- ---------------------------------------------

SELECT * FROM "Customer"."Customer_email" ORDER BY "Customer_id";
SELECT * FROM "Customer"."Customer" c WHERE "User_name" LIKE 'C%';

DELETE FROM "Customer"."Customer_email";

INSERT INTO "Customer"."Customer_email" ("Customer_id", "Entity_id", "Template")
SELECT c.id, b.id, 'bienvenida'  
FROM "Customer"."Customer" c
INNER JOIN "Booking"."Booking" b on b."Customer_id" = c.id
WHERE "User_name" LIKE 'C%'
AND b."Status" <> 'finalizada';

-- ---------------------------------------------
-- Contratos
-- ---------------------------------------------

-- 41 + 12 contratos >= 06/11/2023
SELECT count(*) FROM "Booking"."Booking" b WHERE "Date_from" > '2023-11-06';
SELECT count(*) FROM "Booking"."Booking_group" b WHERE "Date_from" > '2023-11-06';

SELECT id, * FROM "Booking"."Booking" b WHERE "Contract_signed" IS NOT NULL;
SELECT id, * FROM "Booking"."Booking_group" b WHERE "Contract_signed" IS NOT NULL;

-- Pending
SELECT "Status", count(*) FROM "Booking"."Booking" b WHERE "Contract_rent" IS NULL AND "Date_from" >= '2023-11-06' GROUP BY 1;
SELECT "Status", count(*) FROM "Booking"."Booking_group" b WHERE "Contract_rent" IS NULL AND "Date_from" >= '2023-11-06' GROUP BY 1;

-- Delete contracts
UPDATE "Booking"."Booking" b SET "Contract_rent" = null, "Contract_services" = null;
UPDATE "Booking"."Booking_group" b SET "Contract_rent" = null, "Contract_services" = null;

-- ---------------------------------------------
-- Bills estimation
-- ---------------------------------------------

SELECT sum("Qty"), sum("Rent"), sum("Services"), sum("Rent") + sum("Services")
FROM (
  SELECT "Code", sum("Qty") AS "Qty", sum("Rent") AS "Rent", sum("Services") AS "Services"
  FROM (
    SELECT
      substring(r."Code", 1, 6) AS "Code",
      count(*) AS "Qty",
      sum(bp."Rent" + coalesce(bp."Rent_discount", 0)) AS "Rent",
      sum(bp."Services" + coalesce(bp."Services_discount", 0)) AS "Services"
    FROM 
      "Booking"."Booking_price" bp 
      INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
      INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id" 
    WHERE 
      bp."Rent_date" = '2023-11-01'
      AND b."Status" <> 'finalizada'     -- Finalizada por error
      AND b."Date_from" <= '2023-11-01'  -- Aun no han entrado
    GROUP BY 1
    UNION ALL
    SELECT
      bu."Code",
      count(*) AS "Qty",
      sum(b."Rooms" * bp."Rent") AS "Rent",
      sum(b."Rooms" * bp."Services") AS "Services"
    FROM 
      "Booking"."Booking_group_price" bp 
      INNER JOIN "Booking"."Booking_group" b ON b.id = bp."Booking_id" 
      INNER JOIN "Building"."Building" bu on bu.id = b."Building_id"  
    WHERE 
      bp."Rent_date" = '2023-11-01'
    GROUP BY 1
  ) AS "Prices"
  GROUP BY 1
  ORDER BY 1
) AS "Totals";

-- ---------------------------------------------
-- Bills
-- ---------------------------------------------

-- Borrar facturas y pagos
SET myapp.admin='true';
UPDATE "Billing"."Invoice" SET "Issued" = FALSE, "Code" = NULL;
DELETE FROM "Billing"."Invoice_line";
DELETE FROM "Billing"."Invoice";
DELETE FROM "Billing"."Payment";
DELETE FROM "Provider"."Provider_bill";
ALTER SEQUENCE "Billing"."Invoice_id_seq" RESTART WITH 1;
ALTER SEQUENCE "Billing"."Invoice_line_id_seq" RESTART WITH 1;
ALTER SEQUENCE "Billing"."Payment_id_seq" RESTART WITH 1;

-- Total facturado
select sum(i."Total")
from "Billing"."Invoice" i;

-- Cargos sin factura
select b."Status", bp."Rent_date", b."Date_from", b."Date_to", b."Check_out", *
from "Booking"."Booking_price" bp 
inner join "Booking"."Booking" b on b.id = bp."Booking_id" 
inner join "Resource"."Resource" r on r.id = b."Resource_id" 
inner join "Building"."Building" bu on bu.id = r."Building_id"  
left join "Billing"."Invoice" i on i.id = bp."Invoice_rent_id" 
where bp."Rent_date" = '2023-11-01'
and i.id is null;

-- Numeraci�n
select p."Name", pb."Bill_number", min(i."Code"), max(i."Code"), count(*)
from "Billing"."Invoice" i 
inner join "Provider"."Provider" p on p.id = i."Provider_id"
inner join "Provider"."Provider_bill" pb on pb."Provider_id" = p.id
group by 1, 2
order by 1

-- ---------------------------------------------
-- Pagos 
-- ---------------------------------------------

select *
from "Billing"."Payment" p 
where p."Payment_date" is not null;

-- ---------------------------------------------
-- Reservas mal 
-- ---------------------------------------------

-- Checkout en el pasado, fecha fin en el futuro
select b.id, r."Code", c."Name", b."Date_from", b."Date_to", b."Check_out" 
from "Booking"."Booking" b
inner join "Resource"."Resource" r on r.id = b."Resource_id"
inner join "Customer"."Customer" c on c.id = b."Customer_id" 
where b."Check_out" < now() 
and b."Date_to" > now();

-- ---------------------------------------------
-- Dynamic web queries 
-- ---------------------------------------------

-- Rooms
SELECT 
  b."Code" AS "Building_code", rpt."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code", 
  b."Name" AS "Building_name", rpt."Name" AS "Place_type_name", rft."Name" AS "Flat_type_name", 
  ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0) AS "Price", MIN(mrt.id) AS "Photo"
FROM "Resource"."Resource" r
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
  INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
  INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
  INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
  INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Place_type_id" = rpt.id)
  LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2024-01-31' AND bd."Date_to" >= '2023-11-01')
WHERE bd.id IS NULL 
  AND pd."Year" = 2024 
  AND b."Segment_id" = 1
  AND b."Building_type_id" < 3
  AND d."Location_id" = 1
GROUP BY 1, 2, 3, 4, 5, 6, 7

-- Flats
SELECT 
  b."Code" AS "Building_code", rfst."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code",
  b."Name" AS "Building_name", rfst."Name" AS "Place_type_name", rft."Name" AS "Flat_type_name",
  ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0) AS "Price", MIN(mrt.id) AS "Photo"
FROM 
  "Resource"."Resource" r
  INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
  INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
  INNER JOIN "Resource"."Resource_flat_subtype" rfst ON r."Flat_subtype_id" = rfst.id
  INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
  INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" IS NULL 
  INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Flat_subtype_id" = rfst.id)
  LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= '2024-01-31' AND bd."Date_to" >= '2023-11-01')
WHERE bd.id IS NULL 
  AND pd."Year" = 2024
  AND b."Segment_id" = 1
  AND b."Building_type_id" < 3
  AND d."Location_id" = 1
GROUP BY 1, 2, 3, 4, 5, 6, 7
ORDER BY 1, 2;
;

-- ---------------------------------------------
-- SAP API 
-- ---------------------------------------------

SELECT DISTINCT "Type", "case" AS "Third_party", "Document", "Name", "Address", "Zip", "City", "Province", "Code" AS "Country", "Email"
FROM (
  SELECT c."Type", CASE WHEN r."Owner_id" = 10 THEN 'true' ELSE 'false' END CASE, c."Document", c."Name", c."Address", c."Zip", c."City", c."Province", co."Code" , c."Email"
  FROM "Booking"."Booking_price" bp
  INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id" 
  INNER JOIN "Customer"."Customer" c on c.id = b."Customer_id" 
  INNER JOIN "Geo"."Country" co on co.id = c."Country_id" 
  WHERE (c."Created_at" > '2023-01-01' OR c."Updated_at" > '2023-01-01')
  UNION ALL
  SELECT c."Type", CASE WHEN r."Owner_id" = 10 THEN 'true' ELSE 'false' END CASE, c."Document", c."Name", c."Address", c."Zip", c."City", c."Province", co."Code" , c."Email"
  FROM "Booking"."Booking_group_rooming" br
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

-- Tipolog�AS de habitaciones en piso compartido
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
  AND rpt."Code" NOT LIKE 'DUI_%'
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
    
-- Tipolog�AS de apartamentos privados
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
UPDATE "Booking"."Booking_group_rooming" SET id=id;
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'piso';
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'habitacion';
UPDATE "Resource"."Resource" SET id=id WHERE "Resource_type" = 'plaza';
UPDATE "Resource"."Resource_availability" SET id=id;
UPDATE "Billing"."Payment" SET id=id;
UPDATE "Billing"."Invoice" SET "Rectified"=FALSE;
UPDATE "Provider"."Provider" SET id=id;
UPDATE "Customer"."Customer" SET "User_name" = NULL WHERE id=916;
UPDATE "Customer"."Customer_email" SET "Sent_at" = NULL, "Body" = NULL, "Subject" = NULL;
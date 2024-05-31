SELECT
  CONCAT('CRX', il.id) AS "id",
  i.id AS "doc_id",
  i."Bill_type" AS "doc_type",
  b.id AS "booking",
  i."Issued_date" AS "date",
  p."Document" AS "provider", 
  i."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
    WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
    ELSE 'LONG'
  END AS "stay_length",
  CASE
    WHEN pr."Product_type_id" <> 3 AND i."Provider_id" <> 1 THEN 'Monthly rent'
    ELSE pr."Name_en"
  END "product",
  il."Amount" / (1 + (t."Value" / 100)) AS "amount",
  CASE 
    WHEN i."Rectified" OR i."Bill_type" = 'rectificativa' THEN il."Amount" / (1 + (t."Value" / 100))
    WHEN pr."Product_type_id" = 1 THEN COALESCE(b."Booking_fee", il."Amount") / (1 + (t."Value" / 100))
	  WHEN pr."Product_type_id" = 3 THEN COALESCE(bp."Rent", il."Amount") / (1 + (t."Value" / 100))
	  WHEN pr."Product_type_id" > 3 THEN COALESCE(bp."Services", il."Amount") / (1 + (t."Value" / 100))
  END AS "rate",
  'B2C' AS "income_type",
  'Real' AS "data_type",
  CASE 
    WHEN pr."Product_type_id" = 1 THEN dtb."Name_en"
    ELSE dtp."Name_en"
   END AS "discount_type"
FROM "Billing"."Invoice_line" il 
  INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id" 
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Booking"."Booking" b ON b.id = i."Booking_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  LEFT JOIN "Booking"."Booking_price" bp ON bp."Invoice_rent_id" = i.id 
  LEFT JOIN "Booking"."Booking_discount_type" dtp ON dtp.id = bp."Discount_type_id"
  LEFT JOIN "Booking"."Booking_discount_type" dtb ON dtb.id = b."Booking_discount_type_id"
WHERE i."Issued" 
  AND i."Issued_date" >= '2024-01-01'
  AND pr."Product_type_id" <> 2
;
	
-- Limpieza final pisos completos, antiguo mecanismo      
SELECT *
FROM (
	SELECT DISTINCT ON (b.id) b.id, bp."Rent_date", bp."Rent", bp."Services" 
	FROM "Booking"."Booking_price" bp
	INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id" 
	INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
	WHERE b."Final_cleaning" <> 0
	  AND r."Owner_id" = 10
	ORDER BY b.id DESC, bp."Rent_date" DESC 
) AS x
WHERE "Services" = 0
;

-- Pagos con el nuevo TPV de Cotown
SELECT p."Payment_auth", p."Concept", * 
FROM "Billing"."Payment" p 
WHERE p."Pos" = 'cotown'
AND p."Payment_method_id" = 1
AND p."Payment_auth" IS NOT NULL
AND p."Payment_date" > '2024-05-28'
ORDER BY p."Payment_date" DESC 
;

--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B6_checkin";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B0_audit_insert";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B1_init";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_A2_update_availability";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B2_validate";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B3_calc_prices";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B4_workflow";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_B5_buttons";
--ALTER TABLE "Booking"."Booking" DISABLE TRIGGER "Booking_A1_init";
--UPDATE "Booking"."Booking"
--SET id = id;
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B6_checkin";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B0_audit_insert";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B1_init";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_A2_update_availability";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B2_validate";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B3_calc_prices";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B4_workflow";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_B5_buttons";
--ALTER TABLE "Booking"."Booking" ENABLE TRIGGER "Booking_A1_init";

-- All places
SELECT r.id, b."Name" AS "Building", r."Code" AS "Resource"
FROM "Resource"."Resource" r 
INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
WHERE r."Resource_type" = 'plaza'
UNION
-- All rooms without places
SELECT r.id, b."Name" AS "Building", r."Code" AS "Resource"
FROM "Resource"."Resource" r 
INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
WHERE "Resource_type" = 'habitacion' AND 
NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Room_id" = r.id)
UNION
-- All Flats without rooms
SELECT r.id, b."Name" AS "Building", r."Code" AS "Resource"
FROM "Resource"."Resource" r 
INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
WHERE "Resource_type" = 'piso' AND 
NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Flat_id" = r.id)
ORDER BY 3
;

SELECT *
FROM "Booking"."Booking_answer" ba
INNER JOIN "Booking"."Booking_question" bq ON bq.id = ba."Question_id" 
WHERE bq."Question_type" = 'puntos'
AND ba."Answer" < '3'
;

SELECT pt."Name_en", p."Name" 
FROM "Billing"."Product" p 
INNER JOIN "Billing"."Product_type" pt ON pt.id = p."Product_type_id"
WHERE pt.id <> 2
ORDER BY 1, 2
;
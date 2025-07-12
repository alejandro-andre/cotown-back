-- Gestiona la historia de precios de los recursos
DECLARE

  res RECORD;
  ano INTEGER;
  rec RECORD;
  cur RECORD;

BEGIN

  -- Año académico (septiembre a agosto)
  ano := EXTRACT(YEAR FROM CURRENT_DATE);
  IF EXTRACT(MONTH FROM CURRENT_DATE) > 8 THEN
    ano := ano + 1;
  END IF;

  -- Iterar todos los recursos
  FOR res IN
    SELECT 
      r.id, 
      r."Code",
	  r."Building_id",
	  r."Flat_type_id",
	  r."Place_type_id",
      r."Rate_id",
      CASE 
        WHEN pr."Multiplier" <= 0 THEN 1
        ELSE pr."Multiplier" 
      END AS "Multiplier"
    FROM "Resource"."Resource" r 
      INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
  LOOP
    -- Obtener precios base desde Pricing_detail
    SELECT *
    INTO rec
    FROM "Billing"."Pricing_detail" pd
    WHERE pd."Year" = ano
      AND pd."Building_id" = res."Building_id"
      AND pd."Flat_type_id" = res."Flat_type_id"
      AND pd."Place_type_id" = res."Place_type_id";
    IF NOT FOUND THEN
      CONTINUE;
    END IF;

    -- Obtener último precio
    SELECT *
    INTO cur
    FROM "Resource"."Resource_price"
    WHERE "Resource_id" = res.id
    ORDER BY "Date_price" DESC
    LIMIT 1;

    IF NOT FOUND 
       OR res."Rate_id" IS DISTINCT FROM cur."Rate_id"
       OR ROUND(rec."Rent_short" * res."Multiplier", 2) IS DISTINCT FROM cur."Rent_short"
       OR ROUND(rec."Rent_medium" * res."Multiplier", 2) IS DISTINCT FROM cur."Rent_medium"
       OR ROUND(rec."Rent_long" * res."Multiplier", 2) IS DISTINCT FROM cur."Rent_long"
       OR ROUND(rec."Rent_group" * res."Multiplier", 2) IS DISTINCT FROM cur."Rent_group" THEN

      INSERT INTO "Resource"."Resource_price" (
        "Resource_id", "Date_price", "Rate_id",
        "Rent_short", "Rent_medium", "Rent_long", "Rent_group",
        "Services", "Deposit", "Limit", "Final_cleaning", "Booking_fee"
      )
      VALUES (
        res.id, CURRENT_DATE, res."Rate_id",
        ROUND(rec."Rent_short" * res."Multiplier", 2), 
        ROUND(rec."Rent_medium" * res."Multiplier", 2), 
        ROUND(rec."Rent_long" * res."Multiplier", 2), 
        ROUND(rec."Rent_group" * res."Multiplier", 2),
        rec."Services", rec."Deposit", rec."Limit",
        rec."Final_cleaning", rec."Booking_fee"
      )
      ON CONFLICT ("Resource_id", "Date_price") DO UPDATE SET
        "Rate_id" = EXCLUDED."Rate_id",
        "Rent_short" = EXCLUDED."Rent_short",
        "Rent_medium" = EXCLUDED."Rent_medium",
        "Rent_long" = EXCLUDED."Rent_long",
        "Rent_group" = EXCLUDED."Rent_group",
        "Services" = EXCLUDED."Services",
        "Deposit" = EXCLUDED."Deposit",
        "Limit" = EXCLUDED."Limit",
        "Final_cleaning" = EXCLUDED."Final_cleaning",
        "Booking_fee" = EXCLUDED."Booking_fee";

    END IF;

  END LOOP;

END;
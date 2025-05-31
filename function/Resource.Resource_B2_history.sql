-- Gestiona la historia de un recurso
-- BEFORE INSERT/UPDATE
DECLARE

  ano INTEGER;
  rec RECORD;
  cur RECORD;
  curr_user VARCHAR;
  
BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Year
  ano := EXTRACT(YEAR FROM CURRENT_DATE);
  IF (EXTRACT(MONTH FROM CURRENT_DATE) > 8) THEN
    ano := ano + 1;
  END IF;

  -- Get prices from pricing details
  SELECT *
  INTO rec
  FROM "Billing"."Pricing_detail" pd
  WHERE pd."Year" = EXTRACT(YEAR FROM CURRENT_DATE)
    AND pd."Building_id" = NEW."Building_id"
    AND pd."Flat_type_id" = NEW."Flat_type_id"
    AND pd."Place_type_id" = NEW."Place_type_id";

  -- Get last prices
  SELECT *
  INTO cur
  FROM "Resource"."Resource_price"
  WHERE "Resource_id" = NEW.id
  ORDER BY "Date_price" DESC
  LIMIT 1;

  -- Insert history
  IF NOT FOUND 
    OR NEW."Rate_id" <> cur."Rate_id" 
    OR rec."Rent_short" <> cur."Rent_short" 
    OR rec."Rent_medium" <> cur."Rent_medium"
    OR rec."Rent_long" <> cur."Rent_long" THEN
    INSERT INTO "Resource"."Resource_price" ( 
  	  "Resource_id", "Date_price", "Rate_id", 
      "Rent_short", "Rent_medium", "Rent_long", "Services", "Deposit", "Limit", "Final_cleaning", "Booking_fee"
    )
    VALUES (
      NEW.id, CURRENT_DATE, NEW."Rate_id", 
      rec."Rent_short", rec."Rent_medium", rec."Rent_long", rec."Services", rec."Deposit", rec."Limit", rec."Final_cleaning", rec."Booking_fee"
    )
	ON CONFLICT ("Resource_id", "Date_price") DO UPDATE SET 
  	  "Rate_id" = EXCLUDED."Rate_id",
  	  "Rent_short" = EXCLUDED."Rent_short",
  	  "Rent_medium" = EXCLUDED."Rent_medium",
  	  "Rent_long" = EXCLUDED."Rent_long",
  	  "Services" = EXCLUDED."Services",
  	  "Deposit" = EXCLUDED."Deposit",
  	  "Limit" = EXCLUDED."Limit",
  	  "Final_cleaning" = EXCLUDED."Final_cleaning",
  	  "Booking_fee" = EXCLUDED."Booking_fee";
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
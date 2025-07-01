-- Gestiona el pago del check-in
DECLARE 

  holiday INTEGER;
  dow INTEGER;
  num INTEGER; 
  curr_user VARCHAR;
  payment_method_id INTEGER = 1;
  price DECIMAL;
  loc INTEGER;

BEGIN

  -- No changes, no calc
  IF OLD."Check_in_option_id" IS NOT DISTINCT FROM NEW."Check_in_option_id" AND 
     OLD."Check_in"           IS NOT DISTINCT FROM NEW."Check_in"           AND 
     OLD."Check_in_time"      IS NOT DISTINCT FROM NEW."Check_in_time"      THEN
    RETURN NEW;
  END IF;

  -- No option
  IF NEW."Check_in_option_id" IS NULL OR NEW."Resource_id" IS NULL THEN
    NEW."Check_in_option_id" := NULL;
    RETURN NEW;
  END IF;

  -- Check field values
  IF NEW."Check_in" IS NULL THEN
    RAISE EXCEPTION '!!!Must fill check-in date!!!Debes indicar la fecha de check-in!!!';
  END IF;
  IF NEW."Check_in_time" IS NULL THEN
    RAISE EXCEPTION '!!!Must fill check-in time!!!Debes indicar la hora de check-in!!!';
  END IF;

  -- Superuser
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Get booking location
  SELECT d."Location_id"
  INTO loc
  FROM "Resource"."Resource" r 
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Geo"."District" d ON d.id = b."District_id"
  WHERE r.id = NEW."Resource_id";

  -- Get day of week of arrival date
  SELECT extract(dow FROM NEW."Check_in") 
  INTO dow;

  -- Is it holiday?
  SELECT h.id 
  INTO holiday
  FROM "Auxiliar"."Holiday" h 
  WHERE h."Day" = NEW."Check_in"
    AND (h."Location_id" = loc or h."Location_id" is null);

  -- Get holiday prices
  IF holiday IS NOT NULL or dow = 0 THEN
    SELECT cp."Price" 
    INTO price
    FROM "Booking"."Checkin_type" ct 
      INNER JOIN "Booking"."Checkin_price" cp ON cp."Checkin_type_id" = ct.id
      INNER JOIN "Auxiliar"."Timetable" t ON t.id = cp."Timetable_id"
    WHERE ct.id = NEW."Check_in_option_id"
      AND cp."Location_id" = loc
      AND t."Sun_from" IS NOT NULL
      AND NEW."Check_in_time" BETWEEN t."Sun_from" AND t."Sun_to" - interval '1' second;
  END IF;

  -- Get saturday prices
  IF holiday IS NULL AND dow = 6 THEN
    SELECT cp."Price" 
    INTO price
    FROM "Booking"."Checkin_type" ct 
      INNER JOIN "Booking"."Checkin_price" cp ON cp."Checkin_type_id" = ct.id
      INNER JOIN "Auxiliar"."Timetable" t ON t.id = cp."Timetable_id"
    WHERE ct.id = NEW."Check_in_option_id"
      AND cp."Location_id" = loc
      AND t."Sat_from" IS NOT NULL
      AND NEW."Check_in_time" BETWEEN t."Sat_from" AND t."Sat_to" - interval '1' second;
  END IF;

  -- Get friday prices
  IF holiday IS NULL AND dow = 5 THEN
    SELECT cp."Price" 
    INTO price
    FROM "Booking"."Checkin_type" ct 
      INNER JOIN "Booking"."Checkin_price" cp ON cp."Checkin_type_id" = ct.id
      INNER JOIN "Auxiliar"."Timetable" t ON t.id = cp."Timetable_id"
    WHERE ct.id = NEW."Check_in_option_id"
      AND cp."Location_id" = loc
      AND t."Fri_from" IS NOT NULL
      AND NEW."Check_in_time" BETWEEN t."Fri_from" AND t."Fri_to" - interval '1' second;
  END IF;
  
  -- Get weekly prices
  IF holiday IS NULL AND dow BETWEEN 1 AND 4 THEN
    SELECT cp."Price" 
    INTO price
    FROM "Booking"."Checkin_type" ct 
      INNER JOIN "Booking"."Checkin_price" cp ON cp."Checkin_type_id" = ct.id
      INNER JOIN "Auxiliar"."Timetable" t ON t.id = cp."Timetable_id"
    WHERE ct.id = NEW."Check_in_option_id"
      AND cp."Location_id" = loc
      AND t."Week_from" IS NOT NULL
      AND NEW."Check_in_time" BETWEEN t."Week_from" AND t."Week_to" - interval '1' second;
  END IF;

  -- Insert/Update payment
  IF price IS NULL THEN
    RAISE EXCEPTION '!!!Service not available!!!Servicio no disponible!!!';
  END IF;

  -- Check if payment already exists
  SELECT COUNT(*) INTO num 
  FROM "Billing"."Payment" 
  WHERE "Payment_type" = 'checkin'
    AND "Booking_id" = NEW.id;
  IF num > 0 THEN
    RETURN NEW;
  END IF;

  -- Insert fee
  IF price > 0 THEN
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";
    INSERT
      INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
      VALUES (COALESCE(payment_method_id, 1), 'cotown', NEW."Customer_id", NEW.id, price, CURRENT_DATE, 'Check-in', 'checkin');
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
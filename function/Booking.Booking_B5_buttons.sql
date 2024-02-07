-- Botones de reserva
DECLARE

   flat INTEGER;

BEGIN

  -- Avoid recursive calls
  IF pg_trigger_depth() > 1 THEN
    RETURN NEW;
  END IF;

  -- CHA
  IF COALESCE(OLD."Origin_id", 0) <> COALESCE(NEW."Origin_id", 0) THEN
    IF NEW."Origin_id" IS NULL THEN
      UPDATE "Booking"."Booking" SET "Destination_id" = NULL WHERE id = OLD."Origin_id";
    ELSE
      UPDATE "Booking"."Booking" SET "Destination_id" = NEW.id WHERE id = NEW."Origin_id";
    END IF;
  END IF;
  IF COALESCE(OLD."Destination_id", 0) <> COALESCE(NEW."Destination_id", 0) THEN
    IF NEW."Destination_id" IS NULL THEN
      UPDATE "Booking"."Booking" SET "Origin_id" = NULL WHERE id = OLD."Destination_id";
    ELSE
      UPDATE "Booking"."Booking" SET "Origin_id" = NEW.id WHERE id = NEW."Destination_id";
    END IF;
  END IF;

  -- Keyless
  IF OLD."Check_in_keyless_ok" <> TRUE AND NEW."Check_in_keyless_ok" = TRUE AND NEW."Origin_id" IS NULL THEN
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'keyless', NEW.id);
  END IF;

  -- Boton descartar
  NEW."Button_discard" := '';
  IF NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas' OR NEW."Status" = 'pendientepago' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/descartada');
  END IF;
  IF NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/descartadapagada');
  END IF;

  -- Boton checkin
  NEW."Button_checkin" := '';
  IF NEW."Status" = 'checkin' THEN
     NEW."Button_checkin" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/inhouse');
  END IF;

  -- Boton checkout
  NEW."Button_checkout" := '';
  IF NEW."Status" = 'checkout' THEN -- AND pending_payments = 0
     NEW."Button_checkout" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/revision');
  END IF;

  -- Return
  RETURN NEW;

END;
-- Botones de reserva
DECLARE

   flat INTEGER;

BEGIN

  -- CHA
  IF OLD."Destination_id" IS NULL AND NEW."Destination_id" IS NOT NULL THEN
    UPDATE "Booking"."Booking" SET "Origin_id" = NEW.id WHERE id = NEW."Destination_id" AND "Origin_id" <> NEW.id;
  END IF;
  IF OLD."Origin_id" IS NULL AND NEW."Origin_id" IS NOT NULL THEN
    UPDATE "Booking"."Booking" SET "Destination_id" = NEW.id WHERE id = NEW."Origin_id" AND "Destination_id" <> NEW.id;
  END IF;

  -- Keyless
  IF OLD."Check_in_keyless_ok" <> TRUE AND NEW."Check_in_keyless_ok" = TRUE THEN
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
     NEW."Button_checkout" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/devolvergarantia');
  END IF;

  -- Return
  RETURN NEW;

END;
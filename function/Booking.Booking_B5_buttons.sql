-- Botones de reserva
DECLARE

   flat INTEGER;

BEGIN

  -- Aviso a compañeros
  IF OLD."Check_in_notice_ok" <> TRUE AND NEW."Check_in_notice_ok" = TRUE THEN
    -- Get flat
    SELECT r."Flat_id" INTO flat
    FROM "Booking"."Booking" b INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    WHERE b.id = NEW.id;

    -- Get roommates
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      SELECT c.id, 'compis', NEW.id
      FROM "Booking"."Booking" b
        INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      WHERE b.id <> NEW.id
        AND r."Flat_id" = flat
        AND COALESCE(b."Check_in", b."Date_from") <= COALESCE(NEW."Check_in", NEW."Date_from")
        AND COALESCE(b."Check_out", b."Date_to") > COALESCE(NEW."Check_in", NEW."Date_from");
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
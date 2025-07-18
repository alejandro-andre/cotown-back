-- Inserta en blanco los precios de la reserva
DECLARE

  dt_to DATE;
  dt_curr DATE;
  num INTEGER;

BEGIN

  -- Only calc if not yet confirmed or no calculated yet
  SELECT COUNT(*) 
  INTO num
  FROM "Booking"."Booking_group_price"
  WHERE "Booking_id" = NEW.id;
  IF num > 0 AND NEW."Status" <> 'grupobloqueado' THEN
    RETURN NEW;
  END IF;

  -- Borra viejos fuera de los margenes del contrato
  DELETE FROM "Booking"."Booking_group_price"
  WHERE "Booking_id" = NEW.id
  AND ("Rent_date" < NEW."Date_from" OR "Rent_date" > NEW."Date_to");

  -- Inserta precios si no existen ya
  dt_curr = NEW."Date_from";
  dt_to = NEW."Date_to" + INTERVAL '1 day';
  WHILE dt_curr < dt_to LOOP
    BEGIN
      INSERT INTO "Booking"."Booking_group_price" ("Booking_id", "Rent_date", "Rent", "Services") VALUES (NEW.id, dt_curr, NEW."Rent", NEW."Services");
    EXCEPTION WHEN unique_violation THEN
      NULL;
    END;
    dt_curr := date_trunc('month', dt_curr) + INTERVAL '1 month';
  END LOOP;

  -- Return
  RETURN NEW;

END;
-- Inserta en blanco los precios de la reserva
DECLARE

  dt_to DATE;
  dt_curr DATE;

BEGIN

  RESET ROLE;
  
  -- Insert prices
  dt_curr = NEW."Date_from";
  dt_to = NEW."Date_to" + INTERVAL '1 day';
  WHILE dt_curr < dt_to LOOP
    BEGIN
      INSERT INTO "Booking"."Booking_price" ("Booking_id", "Rent_date", "Rent", "Services") VALUES (NEW.id, dt_curr, 0, 0);
    EXCEPTION WHEN unique_violation THEN
      NULL;
    END;
    dt_curr := date_trunc('month', dt_curr) + INTERVAL '1 month';
  END LOOP;

  -- Return
  RETURN NEW;

EXCEPTION
  WHEN OTHERS THEN
    RETURN OLD;

END;
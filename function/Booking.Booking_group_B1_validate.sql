-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;
  billing_type VARCHAR;

BEGIN

  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;
  IF NEW."Date_from" > (SELECT MIN("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents before initial date!!!Hay rentas anteriores a la fecha de inicio!!!';
  END IF;
  IF NEW."Date_to" < (SELECT MAX("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents after finish date!!!Hay rentas posteriores a la fecha de fin!!!';
  END IF;

  -- Check the places
  IF (NEW."Rooms" IS NULL OR NEW."Rooms" < 1) THEN
    RAISE exception '!!!Enter the number of places!!!Introduzca el número de plazas!!!';
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Billing type
  IF NEW."Building_id" IS NOT NULL AND NEW."Billing_type" IS NULL THEN
    SELECT "Billing_type" INTO billing_type 
    FROM "Resource"."Resource" 
    WHERE "Building_id" = NEW."Building_id" AND "Billing_type" <> 'na' 
    ORDER BY id LIMIT 1;
    NEW."Billing_type" = billing_type;
  END IF;

  -- Return record
  RETURN NEW;

END;
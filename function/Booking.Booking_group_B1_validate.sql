-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;
  num INTEGER;
  billing_type VARCHAR;

BEGIN

  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;
  IF NEW."Date_from" > (SELECT MIN("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents before initial date!!!Hay rentas anteriores a la fecha de inicio!!!';
  END IF;
  IF NEW."Date_from" > (SELECT MIN("Check_in") FROM "Booking"."Booking_group_rooming" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Check-ins before initial date!!!Hay check-ins anteriores a la fecha de inicio!!!';
  END IF;
  IF NEW."Date_to" < (SELECT MAX("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents after finish date!!!Hay rentas posteriores a la fecha de fin!!!';
  END IF;
  IF NEW."Date_to" < (SELECT MAX("Check_out") FROM "Booking"."Booking_group_rooming" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Check-outs after finish date!!!Hay check-outs posteriores a la fecha de fin!!!';
  END IF;

  -- Check the places
  IF (NEW."Rooms" IS NULL OR NEW."Rooms" < 1) THEN
    RAISE exception '!!!Enter the number of places!!!Introduzca el número de plazas!!!';
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Cannot cancel booking with invoices
  IF NEW."Status" = 'cancelada' THEN
  	SELECT COUNT(*)
  	INTO num
  	FROM "Billing"."Invoice" i
  	WHERE i."Booking_group_id" = NEW.id;
    IF num > 0 THEN
      RAISE exception '!!!Cannot cancel booking with invoices!!!No se puede cancelar una reserva con facturas!!!';
    END IF;
  END IF;

  -- Billing type
  IF NEW."Building_id" IS NOT NULL AND (NEW."Billing_type" IS NULL OR NEW."Billing_type_last" IS NULL ) THEN
    SELECT "Billing_type" INTO billing_type 
    FROM "Resource"."Resource" 
    WHERE "Building_id" = NEW."Building_id" AND "Billing_type" <> 'na' 
    ORDER BY id LIMIT 1;
    IF NEW."Billing_type" IS NULL THEN
      NEW."Billing_type" = billing_type;
    END IF;
    IF NEW."Billing_type_last" IS NULL THEN
      NEW."Billing_type_last" = billing_type;
    END IF;
  END IF;

  -- Return record
  RETURN NEW;

END;
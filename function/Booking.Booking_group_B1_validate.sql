-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;

BEGIN

  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;

  -- Check the places
  IF (NEW."Rooms" IS NULL OR NEW."Rooms" < 1) THEN
    RAISE exception '!!!Enter the number of places!!!Introduzca el número de plazas!!!';
  END IF;

  -- Check the Rent is not null
  IF (NEW."Rent" IS NULL ) THEN
    RAISE exception '!!!Enter the amount of rent!!!Introduzca el importe de la renta!!!';
  END IF;

  -- Check the Services is not null
  IF (NEW."Services" IS NULL ) THEN
    RAISE exception '!!!Enter the services of rent!!!Introduzca el importe de los servicios!!!';
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Return record
  RETURN NEW;

END;
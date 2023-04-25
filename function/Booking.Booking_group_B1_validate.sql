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

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Return record
  RETURN NEW;

END;
-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;

BEGIN

  -- Locked booking
  IF NEW."Lock" AND 
    OLD."Resource_id" IS NOT NULL AND
    OLD."Resource_id" <> NEW."Resource_id" THEN
    RAISE exception '!!!Locked booking!!!Reserva bloqueada!!!';
  END IF;

  -- Resource removed
  IF NEW."Status" NOT IN ('solicitud', 'solicitudpagada', 'alternativas', 'alternativaspagada') AND
    NEW."Resource_id" IS NULL THEN
    RAISE exception '!!!Resource cannot be removed!!!El recurso no se puede quitar!!!';
  END IF;

  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;

  -- Validate checkin checkout dates
  IF NEW."Check_in" IS NOT NULL THEN
    IF NEW."Check_in" < NEW."Date_from"THEN
      RAISE exception '!!!Check-in date cannot be earlier than the start of the reservation!!!Fecha de check in no puede ser anterior al inicio de la reserva!!!';
    END IF;
    IF NEW."Check_in" >= NEW."Date_to"THEN
      RAISE exception '!!!Check-in date cannot be later than the end of the reservation!!!Fecha de check in no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;
  IF NEW."Check_out" IS NOT NULL THEN
    IF NEW."Check_out" < NEW."Check_in"THEN
      RAISE exception '!!!Check-out date cannot be earlier than the check-in date!!!Fecha de check out no puede ser anterior al check-in!!!';
    END IF;
    IF NEW."Check_out" >= NEW."Date_to"THEN
      RAISE exception '!!!Check-out date cannot be later than the end of the reservation!!!Fecha de check out no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Valida que las fechas de solicitud sea menor que la fecha de expiracion
  IF NEW."Expiry_date" IS NOT NULL THEN
    IF NEW."Expiry_date" < NEW."Request_date"· THEN
      RAISE EXCEPTION '!!!The expiry date must be equal to or greater than the date of application.!!!La fecha de expiración debe ser igual o mayor a la fecha de solicitud!!!';
    END IF;
  END IF;

  -- Payer
  IF NEW."Payer_id" IS NULL THEN
    NEW."Payer_id" = NEW."Customer_id";
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Validate duration
  --SELECT AGE(NEW."Date_to" + INTERVAL '1 day', NEW."Date_from") INTO duration;
  --SELECT EXTRACT(YEAR FROM duration) INTO years;
  --SELECT EXTRACT(MONTH FROM duration) INTO months;
  --SELECT EXTRACT(DAY FROM duration) INTO days;
  --IF years > 0 OR months > 11 OR (months = 11 AND days > 0) THEN
  --  RAISE exception '!!!The stay should be maximun 11 months long!!!La estancia debe ser como máximo de 11 meses!!!';
  --ELSE
  --  IF months < 1 THEN
  --    RAISE exception '!!!The stay should be at least 1 month long!!!La estancia debe ser de un mes o superior!!!';
  --  END IF;
  --END IF;

  -- Return record
  RETURN NEW;

END;
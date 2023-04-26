-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;

BEGIN

  -- Reserva bloqueada?
  IF NEW."Lock" AND 
    OLD."Resource_id" IS NOT NULL AND
    OLD."Resource_id" <> NEW."Resource_id" THEN
    RAISE exception '!!!Locked booking!!!Reserva bloqueada!!!';
  END IF;

  -- Se ha quitado el recurso y ya está confirmada?
  IF NEW."Status" NOT IN ('solicitud', 'solicitudpagada', 'alternativas', 'alternativaspagada') AND
    NEW."Resource_id" IS NULL THEN
    RAISE exception '!!!Resource cannot be removed!!!El recurso no se puede quitar!!!';
  END IF;

  -- Verifica las fechas
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;

  -- Valida que las fechas de checkin estén en el rango correcto
  IF NEW."Check_in" IS NOT NULL THEN
    IF NEW."Check_in" < NEW."Date_from"THEN
      RAISE exception '!!!Check-in date cannot be earlier than the start of the reservation!!!Fecha de check in no puede ser anterior al inicio de la reserva!!!';
    END IF;
    IF NEW."Check_in" >= NEW."Date_to"THEN
      RAISE exception '!!!Check-in date cannot be later than the end of the reservation!!!Fecha de check in no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Valida que las fechas de checkout estén en el rango correcto
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

  -- Si no hay pagador, es el cliente
  IF NEW."Payer_id" IS NULL THEN
    NEW."Payer_id" = NEW."Customer_id";
  END IF;

  -- Fecha de solicitud
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Return record
  RETURN NEW;

END;
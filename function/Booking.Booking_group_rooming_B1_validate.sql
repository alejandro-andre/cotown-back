-- Verifica los datos de la reserva
DECLARE

  date_from DATE;
  date_to DATE;

BEGIN
	
  -- Fechas de la reserva
  SELECT "Date_from", "Date_to"
  INTO date_from, date_to
  FROM "Booking"."Booking_group"
  WHERE id = NEW."Booking_id";

  -- Verifica las fechas de la habitación
  IF NEW."Check_in" < '2000-01-01' THEN
    NEW."Check_in" = NULL;
  END IF;
  IF NEW."Check_out" < '2000-01-01' THEN
    NEW."Check_out" = NULL;
  END IF;

  -- Valida que las fechas de checkin estén en el rango correcto
  IF NEW."Check_in" IS NOT NULL THEN
    IF NEW."Check_in" < date_from THEN
      RAISE exception '!!!Check-in date cannot be earlier than the start of the reservation!!!Fecha de check in no puede ser anterior al inicio de la reserva!!!';
    END IF;
    IF NEW."Check_in" >= date_to THEN
      RAISE exception '!!!Check-in date cannot be later than the end of the reservation!!!Fecha de check in no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Valida que las fechas de checkout estén en el rango correcto
  IF NEW."Check_out" IS NOT NULL THEN
    IF NEW."Check_out" < NEW."Check_in" THEN
      RAISE exception '!!!Check-out date cannot be earlier than the check-in date!!!Fecha de check out no puede ser anterior al check-in!!!';
    END IF;
    IF NEW."Check_out" > date_to THEN
      RAISE exception '!!!Check-out date cannot be later than the end of the reservation!!!Fecha de check out no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Return record
  RETURN NEW;

END;
-- Precios y descuentos
DECLARE

  date_from DATE;
  date_to DATE;

BEGIN
	
  -- Fechas de la reserva
  SELECT "Date_from", "Date_to"
  INTO date_from, date_to
  FROM "Booking"."Booking_group"
  WHERE id = NEW."Booking_id";

  -- Valida que las fechas está en el rango correcto
  IF NEW."Rent_date" < date_from THEN
    RAISE exception '!!!Date cannot be earlier than the start of the reservation!!!Fecha no puede ser anterior al inicio de la reserva!!!';
  END IF;
  IF NEW."Rent_date" >= date_to THEN
    RAISE exception '!!!Date cannot be later than the end of the reservation!!!Fecha no puede ser posterior al final de la reserva!!!';
  END IF;

  -- Return record
  RETURN NEW;

END

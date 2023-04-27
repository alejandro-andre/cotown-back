-- Valida las fechas
-- BEFORE INSERT/UPDATE
DECLARE

	count INTEGER;

BEGIN

  IF NEW."Date_to" <= NEW."Date_from" THEN
    RAISE EXCEPTION '!!!End date must be greater than start date.!!!La fecha final debe ser mayor o igual que la fecha de inicio.!!!';
  END IF;
 
  SELECT COUNT(*)
  INTO count
  FROM "Booking"."Booking_detail" bd 
  WHERE bd."Date_from" <= NEW."Date_to" 
  AND bd."Date_to" >= NEW."Date_from";

  IF count > 0 THEN
    RAISE EXCEPTION '!!!Lock overlaps with active bookings!!!El bloqueo se solapa con reservas activas!!!';
  END IF;
 
  RETURN NEW;

END;

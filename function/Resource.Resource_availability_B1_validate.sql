-- Valida las fechas
-- BEFORE INSERT/UPDATE
DECLARE

  count INTEGER;

BEGIN

  -- Cosharing is the preset state, do not save
  IF NEW."Status_id" = 1 THEN
    RAISE EXCEPTION '!!!Cosharing is the preset state!!!Cosharing es el estado por defecto!!!';
  END IF;

  -- Valida las fechas
  IF NEW."Date_to" <= NEW."Date_from" THEN
    RAISE EXCEPTION '!!!End date must be greater than start date.!!!La fecha final debe ser mayor o igual que la fecha de inicio.!!!';
  END IF;

  -- Cuenta reservas en este recurso en las mismas fechas
  --?SELECT COUNT(*)
  --?INTO count
  --?FROM "Booking"."Booking_detail" bd
  --?INNER JOIN "Resource"."Resource" r ON r.id = bd."Resource_id"
  --?WHERE "Date_from" <= NEW."Date_to"
  --?AND "Availability_id" IS NULL
  --?AND "Date_to" >= NEW."Date_from"
  --?AND r."Flat_id" = NEW."Resource_id";
  --?IF count > 0 THEN
  --?  RAISE EXCEPTION '!!!Locks overlap with active bookings in this flat!!!Bloqueos se solapan con reservas activas en este piso!!!';
  --?END IF;

  RETURN NEW;

END;
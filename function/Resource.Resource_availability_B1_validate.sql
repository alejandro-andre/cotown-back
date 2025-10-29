-- Valida las fechas
-- BEFORE INSERT/UPDATE/DELETE
DECLARE

  count INTEGER;
  canchange VARCHAR;

BEGIN

  -- No deja modificar bloqueos LAU
  canchange := COALESCE(current_setting('core.allow_lock_change', true), 'false');
  IF TG_OP = 'DELETE' THEN
    IF OLD."Booking_id" IS NOT NULL AND canchange = 'false' THEN
      RAISE EXCEPTION '!!!Cannot change LAU bookings locks!!!NO se pueden modificar bloqueos de reservas LAU!!!';
    ELSE
      RETURN OLD;
    END IF;
  END IF;
  IF TG_OP = 'UPDATE' AND NEW."Booking_id" IS NOT NULL AND canchange = 'false' THEN
    RAISE EXCEPTION '!!!Cannot change LAU bookings locks!!!NO se pueden modificar bloqueos de reservas LAU!!!';
  END IF;

  -- Cosharing is the preset state, do not save
  IF NEW."Status_id" = 1 THEN
    RAISE EXCEPTION '!!!Cosharing is the preset state!!!Cosharing es el estado por defecto!!!';
  END IF;

  -- Valida las fechas
  IF NEW."Date_to" <= NEW."Date_from" THEN
    RAISE EXCEPTION '!!!End date must be greater than start date!!!La fecha final debe ser mayor o igual que la fecha de inicio!!!';
  END IF;

  RETURN NEW;

END;
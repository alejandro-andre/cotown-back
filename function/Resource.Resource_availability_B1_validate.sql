-- Valida las fechas
-- BEFORE INSERT/UPDATE/DELETE
DECLARE

  count INTEGER;

BEGIN

  -- No deja borrar bloqueos LAU
  IF TG_OP = 'DELETE' THEN
    IF OLD."Booking_id" IS NOT NULL AND current_setting('core.allow_lock_delete', true) IS DISTINCT FROM 'true' THEN
      RAISE EXCEPTION '!!!Cannot delete LAU bookings locks!!!NO se pueden borrar bloqueos de reservas LAU!!!';
    ELSE
      RETURN OLD;
    END IF;
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

END;$function$
;

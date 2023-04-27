-- Valida las fechas
-- BEFORE INSERT/UPDATE
BEGIN

  IF NEW."Date_to" <= NEW."Date_from" THEN
    RAISE EXCEPTION '!!!End date must be greater than start date.!!!La fecha final debe ser mayor o igual que la fecha de inicio.!!!';
  END IF;

  RETURN NEW;

END;
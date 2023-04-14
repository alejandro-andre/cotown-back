-- Validate that the 'Unavailability' start and end dates are correct. validateResourceAvailabilityDates
BEGIN
  IF NEW."Date_to" < NEW."Date_from" THEN
    RAISE EXCEPTION '!!!Until date must be greater or equal than start date.!!!La fecha de Hasta debe ser mayor o igual que la fecha de inicio.!!!';
  END IF;
  RETURN NEW;
END;
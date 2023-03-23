-- Validate that the 'Unavailability' start and end dates are correct. validateResourceAvailabilityDates
BEGIN

	IF NEW."DateFrom" < current_date THEN
		RAISE EXCEPTION '!!!The From date must be greater or equal than the current day.!!!La fecha Desde debe ser mayor o igual al día actual.!!!';
	END IF; 

	IF NEW."DateTo" < NEW."DateFrom" THEN
		RAISE EXCEPTION '!!!Until date must be greater or equal than start date.!!!La fecha de Hasta debe ser mayor o igual que la fecha de inicio.!!!';
	END IF;

	RETURN NEW;

END;
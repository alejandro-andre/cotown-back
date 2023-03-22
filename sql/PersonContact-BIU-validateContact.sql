-- Valida que el correo o el telefono este relleno validateContactPhoneEmail
BEGIN

	IF NEW."Email" IS NULL and NEW."Phones" IS NULL THEN
		RAISE EXCEPTION '!!!You must enter the Email and/or the Phone field.!!!Debes introducir el campo Email y/o el campo Teléfono.!!!';
	END IF;

	RETURN NEW;

END;

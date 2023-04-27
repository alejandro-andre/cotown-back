-- Valida que o el correo o el telefono esten rellenos
BEGIN

  IF NEW."Email" IS NULL and NEW."Phones" IS NULL THEN
    RAISE EXCEPTION '!!!You must enter the Email and/or the Phone field.!!!Debes introducir el email y/o elteléfono.!!!';
  END IF;

  RETURN NEW;

END;

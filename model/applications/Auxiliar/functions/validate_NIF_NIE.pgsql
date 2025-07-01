-- Valida el DNI/NIE
DECLARE

  letters TEXT[] := ARRAY['T','R','W','A','G','M','Y','F','P','D','X','B','N','J','Z','S','Q','V','H','L','C','K','E'];
  valid_letter TEXT;

BEGIN

  -- '1' Document type identifier "DNI" from table "Id_type".
  IF NEW."Id_type_id" = 1 THEN
    IF length(NEW."Document") = 9 AND NEW."Document" ~ '^[0-9]{8}[A-Za-z]$' THEN
      valid_letter := letters[(substring(NEW."Document",1,8)::integer % 23) + 1];
      IF valid_letter <> upper(substring(NEW."Document",9,1)) THEN
        RAISE EXCEPTION '!!!The DNI entered is not valid!!!El DNI introducido no es válido.!!!';
      END IF;
    ELSE
      RAISE EXCEPTION '!!!The DNI entered is not valid.!!!Debes introducir un formato de DNI válido.!!!';
    END IF;
  END IF;

  -- '2' Document type identifier "DNI" from table "Id_type".
  IF NEW."Id_type_id" = 2 THEN
    IF length(NEW."Document") <> 9 OR NOT upper(NEW."Document") ~ '^[XYZ]\d{7}[TRWAGMYFPDXBNJZSQVHLCKE]$' THEN
      RAISE EXCEPTION '!!!The NIE entered is not valid.!!!El NIE introducido no es válido.!!!';
    END IF;      
  END IF;

  RETURN NEW;

END;

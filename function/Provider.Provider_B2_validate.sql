-- Verifica el proveedor
DECLARE

  curr_user VARCHAR;
  num INTEGER;
 
BEGIN

  -- Cambio de email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN

    -- Superuser ROLE
    curr_user := CURRENT_USER;
    RESET ROLE; 
  	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";

    IF num > 0 THEN
      RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
    END IF;
    UPDATE "Models"."User" SET email = NEW."Email", password = 'Passw0rd!' WHERE username = NEW."User_name";

    -- Fin
    EXECUTE 'SET ROLE "' || curr_user || '"';

  END IF;

  -- Ok
  RETURN NEW;
 
END;
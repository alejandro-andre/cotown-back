-- Verifica el usuario
DECLARE

  curr_user VARCHAR;
  num INTEGER;
 
BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Cambio de email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
  	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";
    IF num > 0 THEN
      EXECUTE 'SET ROLE "' || curr_user || '"';
      RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
    END IF;
    UPDATE "Models"."User" SET email = NEW."Email" WHERE username = NEW."User_name";
  END IF;

  -- Ok
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;
 
END;
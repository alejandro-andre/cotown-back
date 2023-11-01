-- Verifica el usuario
DECLARE

  curr_user VARCHAR;
  num INTEGER;
 
BEGIN

  -- Cambio de email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
  	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";
    IF num > 0 THEN
      RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
    END IF;
    curr_user := CURRENT_USER;
    RESET ROLE;
    UPDATE "Models"."User" SET email = NEW."Email" WHERE username = NEW."User_name";
    EXECUTE 'SET ROLE "' || curr_user || '"';
  END IF;

  -- Ok
  RETURN NEW;
 
END;
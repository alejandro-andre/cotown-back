-- Verifica el usuario
DECLARE 

 num INTEGER;
 
BEGIN

 -- Cambio de email
 IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
 	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";
   IF num > 0 THEN
     RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
   END IF;
   UPDATE "Models"."User" SET email = NEW."Email" WHERE username = NEW."User_name";
 END IF;

 -- Ok
 RETURN NEW;
 
END;
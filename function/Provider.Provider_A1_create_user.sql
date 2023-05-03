-- Creación de usuario
DECLARE

  user_name VARCHAR;
  user_id INTEGER;

BEGIN

  RESET ROLE;

  -- Username
  user_name := CONCAT('P', LPAD(NEW.id::text, 6, '0'));

  -- Inserta el usuario en Airflows
  INSERT INTO "Models"."User" ("username", "email", "password") 
  VALUES (user_name, NEW."Email", 'Passw0rd!') 
  ON CONFLICT ("username") DO UPDATE SET "email" = NEW."Email"
  RETURNING id INTO user_id;
 
  -- Inserta el rol en Airflows
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (user_id, 200)
  ON CONFLICT ("user", "role") DO NOTHING;

  -- Crea el rol en Postgres
  IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''Passw0rd!'' NOSUPERUSER';
  END IF;
  EXECUTE 'GRANT "provider" TO "' || user_name || '"';

  -- Fin
  RETURN NEW;

  -- Asigna botón
  --IF NEW."User_name" IS NULL AND NEW."Create_user" IS NULL THEN
  --  UPDATE "Provider"."Provider"
  --  SET "Create_user" = CONCAT('https://pre.cotown.ciber.es/provideruser/add/', NEW.id)
  --  WHERE id = NEW.id;
  --END IF;

  -- Borra botón
  --IF NEW."User_name" IS NOT NULL AND NEW."Create_user" IS NOT NULL THEN
  --  UPDATE "Provider"."Provider"
  --  SET "Create_user" = NULL
  --  WHERE id = NEW.id;
  --END IF;

  RETURN NEW;

END;
-- Creación de usuario
DECLARE

  user_name VARCHAR;
  user_id INTEGER;

BEGIN

  RESET ROLE;

  -- Username
  user_name := CONCAT('C', LPAD(NEW.id::text, 6, '0'));

  -- Inserta el usuario en Airflows
  INSERT INTO "Models"."User" ("username", "email", "password") 
  VALUES (user_name, NEW."Email", 'Passw0rd!') 
  ON CONFLICT ("username") DO UPDATE SET "email" = NEW."Email"
  RETURNING id INTO user_id;
 
  -- Inserta el rol en Airflows
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (user_id, 300)
  ON CONFLICT ("user", "role") DO NOTHING;

  -- Crea el rol en Postgres
  IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''Passw0rd!'' NOSUPERUSER';
  END IF;
  EXECUTE 'GRANT "customer" TO "' || user_name || '"';

  -- Fin
  RETURN NEW;

END;
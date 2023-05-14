-- Creación de usuario
-- AFTER INSERT
DECLARE

  user_name VARCHAR;
  user_id INTEGER;

BEGIN

  RESET ROLE;

  -- Username
  user_name := CONCAT('X', LPAD(NEW.id::text, 6, '0'));

  -- Inserta el usuario en Airflows
  INSERT INTO "Models"."User" ("username", "email", "password", "emailValidated") 
  VALUES (user_name, NEW."Email", 'Passw0rd!', FALSE) 
  ON CONFLICT ("username") DO UPDATE SET "email" = NEW."Email"
  RETURNING id INTO user_id;
 
  -- Asigna el usuario
  UPDATE "Admin"."User" SET "User_name" = user_name WHERE id = NEW.id;

  -- Crea el rol en Postgres
  IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''UNK0WN_P4$$W0RD'' NOSUPERUSER';
  END IF;

  -- Fin
  RETURN NEW;

END;
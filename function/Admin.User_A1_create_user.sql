-- Creación de usuario
-- AFTER INSERT
DECLARE

  curr_user VARCHAR;
  user_name VARCHAR;
  user_id INTEGER;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
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

  -- Crea el usuario en Postgres
  IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''UNK0WN_P4$$W0RD'' NOSUPERUSER';
  END IF;

  -- Inserta el rol base (cotown) en Airflows
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (user_id, 100)
  ON CONFLICT ("user", "role") DO NOTHING;

  -- Asigna el rol en Postgres
  EXECUTE 'GRANT "cotown" TO "' || user_name || '"';

  -- Fin
  RETURN NEW;

END;
-- Creación de usuario
DECLARE

  user_name VARCHAR;
  user_id INTEGER;

BEGIN

  RESET ROLE;

  IF NEW."User_name" IS NOT NULL THEN
    RETURN NEW;
  END IF;

  -- Username
  user_name := CONCAT('C', LPAD(NEW.id::text, 6, '0'));

  -- Inserta el usuario en Airflows
  INSERT INTO "Models"."User" ("username", "email", "password") 
  VALUES (user_name, NEW."Email", 'Passw0rd!') 
  ON CONFLICT ("username") DO UPDATE SET "email" = NEW."Email"
  RETURNING id INTO user_id;
 
  -- Inserta el rol en Airflows
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (user_id, 200)
  ON CONFLICT ("user", "role") DO NOTHING;

  -- Asigna el usuario
  UPDATE "Customer"."Customer" SET "User_name" = user_name WHERE id = NEW.id;

  -- Crea el rol en Postgres
  IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''UNK0WN_P4$$W0RD'' NOSUPERUSER';
  END IF;
  EXECUTE 'GRANT "customer" TO "' || user_name || '"';

  -- Email
  INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW.id, 'bienvenida', NEW.id);

  -- Fin
  RETURN NEW;

END;
-- Creación de usuario
DECLARE

 curr_user VARCHAR;
 user_name VARCHAR;
 user_id INTEGER;

BEGIN

 -- Already created
 IF NEW."User_name" IS NOT NULL THEN
   RETURN NEW;
 END IF;

 -- Superuser ROLE
 curr_user := CURRENT_USER;
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

 -- Asigna el usuario
 UPDATE "Provider"."Provider" SET "User_name" = user_name WHERE id = NEW.id;

 -- Crea el rol en Postgres
 IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
   EXECUTE 'CREATE ROLE "' || user_name || '" PASSWORD ''UNK0WN_P4$$W0RD'' NOSUPERUSER';
 END IF;
 EXECUTE 'GRANT "provider" TO "' || user_name || '"';

 -- Fin
 EXECUTE 'SET ROLE "' || curr_user || '"';
 RETURN NEW;

END;
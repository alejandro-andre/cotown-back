-- Asignacion de rol
-- AFTER INSERT
DECLARE 

 user_id INTEGER;
 user_name VARCHAR;
 rol_name VARCHAR;
 curr_user VARCHAR;

BEGIN

 -- Superuser ROLE
 curr_user := CURRENT_USER;
 RESET ROLE;  

 -- Get user name
 SELECT "User_name" INTO user_name FROM "Admin"."User" WHERE id = NEW."User_id";

 -- Inserta el rol en Airflows
 SELECT id INTO user_id FROM "Models"."User" WHERE "username" = user_name;
 INSERT INTO "Models"."UserRole" ("user", "role") VALUES (user_id, NEW."Role_id")
 ON CONFLICT ("user", "role") DO NOTHING;

 -- Asigna el rol
 SELECT "name" INTO rol_name FROM "Models"."Role" WHERE id = NEW."Role_id";
 EXECUTE 'GRANT "' || rol_name || '" TO "' || user_name || '"';

 -- Return
 EXECUTE 'SET ROLE "' || curr_user || '"';
 RETURN NEW;

END;
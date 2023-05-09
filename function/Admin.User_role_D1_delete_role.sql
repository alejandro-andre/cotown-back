-- Desasignacion de rol
-- AFTER DELETE
DECLARE 

  rol_name VARCHAR;
  user_name VARCHAR;
 
BEGIN

  -- Get user name
  SELECT "User_name" INTO user_name FROM "Admin"."User" WHERE id = OLD."User_id";

  -- Borra el rol de Airflows
  DELETE FROM "Models"."UserRole" WHERE "role" = OLD."Role_id" AND "user" = (SELECT id FROM "Models"."User" WHERE "username" = user_name);

  -- Borra el rol
  SELECT "name" INTO rol_name FROM "Models"."Role" WHERE id = OLD."Role_id";
  EXECUTE 'REVOKE "' || rol_name || '" FROM "' || user_name || '"';
 
  -- Return
  RETURN NEW;

END;
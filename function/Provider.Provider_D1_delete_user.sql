-- Borra el usuario y rol de BD del proveedor
-- AFTER DELETE
DECLARE

  user_name VARCHAR;
  
BEGIN

  RESET ROLE;
  user_name := CONCAT('P', OLD.id);
  EXECUTE 'DROP ROLE "' || user_name || '"';
  EXCEPTION WHEN OTHERS THEN NULL;
  DELETE FROM "Models"."User" WHERE "username" = user_name;
  RETURN OLD;

END;
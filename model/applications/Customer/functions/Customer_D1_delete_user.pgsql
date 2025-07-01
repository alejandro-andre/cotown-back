-- Borra el usuario y rol de BD
-- AFTER DELETE
DECLARE

  user_name VARCHAR;
 
BEGIN

  RESET ROLE;
  user_name := CONCAT('C', LPAD(OLD.id::text, 6, '0'));
  DELETE FROM "Models"."User" WHERE "username" = user_name;
  IF EXISTS (SELECT * FROM pg_roles WHERE rolname = user_name) THEN
    EXECUTE 'DROP ROLE "' || user_name || '"';
  END IF;
  RETURN OLD;

END;

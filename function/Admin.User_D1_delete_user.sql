-- Borra el usuario y rol de BD
-- AFTER DELETE
BEGIN

  RESET ROLE;
  DELETE FROM "Models"."User" WHERE "username" = OLD."User_name";
  IF EXISTS (SELECT * FROM pg_roles WHERE rolname = OLD."User_name") THEN
    EXECUTE 'DROP ROLE "' || OLD."User_name" || '"';
  END IF;
  RETURN OLD;

END;

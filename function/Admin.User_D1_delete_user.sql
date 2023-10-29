-- Borra el usuario y rol de BD
-- AFTER DELETE
DECLARE

 curr_user VARCHAR;

BEGIN

 -- Superuser ROLE
 curr_user := CURRENT_USER;
 RESET ROLE;

 -- Delete user
 DELETE FROM "Models"."User" WHERE "username" = OLD."User_name";
 IF EXISTS (SELECT * FROM pg_roles WHERE rolname = OLD."User_name") THEN
   EXECUTE 'DROP ROLE "' || OLD."User_name" || '"';
 END IF;

 -- Return
 EXECUTE 'SET ROLE "' || curr_user || '"';
 RETURN OLD;

END;

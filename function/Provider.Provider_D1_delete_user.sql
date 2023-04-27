-- Borra el usuario y rol de BD del proveedor
-- AFTER DELETE
BEGIN

  RESET ROLE;
  EXECUTE 'DROP ROLE "' || old."User_name" || '"';
  DELETE FROM "Models"."User" WHERE "username" = old."User_name";
  RETURN OLD;

EXCEPTION
  WHEN OTHERS THEN
    RETURN OLD;

END;
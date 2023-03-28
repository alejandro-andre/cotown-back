-- Asigna permisos y rol al usuario
DECLARE
  roleid INTEGER;
  userid INTEGER;
BEGIN
  RESET ROLE;
  SELECT "id" INTO STRICT roleid FROM "Models"."Role" WHERE name = 'provider';
  SELECT "id" INTO STRICT userid FROM "Models"."User" WHERE username = NEW."User_name";
  EXECUTE 'GRANT "user" TO "' || NEW."User_name" || '"';
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (userid, roleid);
  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;
END;
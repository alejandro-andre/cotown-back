--Asigna permisos y rol al usuario y envía mail
DECLARE

  roleid INTEGER;
  userid INTEGER;

BEGIN

  -- Create Role
  RESET ROLE;
  SELECT "id" INTO STRICT roleid FROM "Models"."Role" WHERE name = 'customer';
  SELECT "id" INTO STRICT userid FROM "Models"."User" WHERE username = NEW."User_name";
  EXECUTE 'GRANT "user" TO "' || NEW."User_name" || '"';
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (userid, roleid);

  -- Send email
  INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW.id, 'bienvenida', NEW.id);

  RETURN NEW;

EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;

END;
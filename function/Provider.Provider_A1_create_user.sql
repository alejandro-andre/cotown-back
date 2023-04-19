--Asigna permisos y rol al usuario y envía mail
DECLARE

  roleid INTEGER;
  userid INTEGER;

BEGIN

  RESET ROLE;

  -- Assign username
  NEW."User_name" := 'P' || NEW."Document";
  UPDATE "Provider"."Provider" SET "User_name" = NEW."User_name" WHERE id = NEW.id;

  -- Create DB User
  EXECUTE 'CREATE ROLE "' || NEW."User_name" || '" PASSWORD ''' || NEW."User_name" || 'p4$$w0rd'' NOSUPERUSER';
  INSERT INTO "Models"."User" ("username", "email", "password") VALUES (NEW."User_name", NEW."Email", NEW."User_name" || 'p4$$w0rd')
  RETURNING id INTO userid;

  -- Create DB Role
  SELECT "id" INTO STRICT roleid FROM "Models"."Role" WHERE name = 'provider';
  EXECUTE 'GRANT "user" TO "' || NEW."User_name" || '"';
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (userid, roleid);

  RETURN NEW;

EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;

END;
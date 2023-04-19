--Asigna permisos y rol al usuario y envía mail
DECLARE

  roleid INTEGER;
  userid INTEGER;

BEGIN

  RESET ROLE;

  -- Assign username
  NEW."User_name" := 'C' || LPAD(NEW.id::TEXT, 6, '0');
  UPDATE "Customer"."Customer" SET "User_name" = NEW."User_name" WHERE id = NEW.id;

  -- Create DB User
  EXECUTE 'CREATE ROLE "' || NEW."User_name" || '" PASSWORD ''' || NEW."User_name" || 'p4$$w0rd'' NOSUPERUSER';
  INSERT INTO "Models"."User" ("username", "email", "password") VALUES (NEW."User_name", NEW."Email", NEW."User_name" || 'p4$$w0rd')
  RETURNING id INTO userid;

  -- Create DB Role
  SELECT "id" INTO STRICT roleid FROM "Models"."Role" WHERE name = 'customer';
  EXECUTE 'GRANT "user" TO "' || NEW."User_name" || '"';
  INSERT INTO "Models"."UserRole" ("user", "role") VALUES (userid, roleid);

  -- Send email
  INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW.id, 'bienvenida', NEW.id);

  RETURN NEW;

EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;

END;
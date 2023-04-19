-- Crea el usuario de BD para el proveedor
BEGIN

  RESET ROLE;
  NEW."User_name" := 'C' || LPAD(NEW.id::TEXT, 6, '0');
  EXECUTE 'CREATE ROLE "' || NEW."User_name" || '" PASSWORD ''' || NEW."User_name" || 'p4$$w0rd'' NOSUPERUSER';
  INSERT INTO "Models"."User" ("username", "email", "password") VALUES (NEW."User_name", NEW."Email", NEW."User_name" || 'p4$$w0rd');
  RETURN NEW;

EXCEPTION
  WHEN OTHERS THEN
    RETURN NEW;

END;
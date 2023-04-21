-- Botón de creación de usuario
BEGIN

  -- Asigna botón
  IF NEW."User_name" IS NULL AND NEW."Create_user" IS NULL THEN
    UPDATE "Customer"."Customer"
    SET "Create_user" = CONCAT('https://dev.cotown.ciber.es/customeruser/add/', NEW.id)
    WHERE id = NEW.id;
  END IF;

  -- Borra botón
  IF NEW."User_name" IS NOT NULL AND NEW."Create_user" IS NOT NULL THEN
    UPDATE "Customer"."Customer"
    SET "Create_user" = NULL
    WHERE id = NEW.id;
  END IF;

  RETURN NEW;

END;
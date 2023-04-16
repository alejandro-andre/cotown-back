-- Selecciona un solo contrato activo
BEGIN

  RESET ROLE;

  IF pg_trigger_depth() = 1 AND NEW."Active" = TRUE THEN
    UPDATE "Provider"."Provider_template"
    SET "Active" = FALSE 
    WHERE "Provider_id" = NEW."Provider_id"
    AND "Type" = NEW."Type"
    AND id <> NEW.id;
  END IF;

  RETURN NEW;

END;
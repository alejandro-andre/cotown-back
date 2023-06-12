-- Creación de email
DECLARE

  en BOOLEAN;

BEGIN

  -- Plantilla
  SELECT "Enabled"
  INTO en
  FROM "Admin"."Email" e
  WHERE e."Name" = NEW."Template";
  
  -- Si existe y esta activa
  IF en = TRUE THEN
    RETURN NEW;
  END IF;

  -- Ignora el email
  RETURN NULL;

END;
-- Creación de email
DECLARE

  en BOOLEAN;
  tipo VARCHAR;

BEGIN

  -- Tipo de cliente
  SELECT "Type"
  INTO tipo
  FROM "Customer"."Customer"
  WHERE id = NEW."Customer_id";

  -- Empresa? Ignora
  IF tipo = 'empresa' THEN
    RETURN NULL;
  END IF;

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
  --RAISE NOTICE 'EMAIL % A % IGNORADO', NEW."Template", NEW."Customer_id";
  RETURN NULL;

END;
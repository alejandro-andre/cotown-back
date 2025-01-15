-- Creación de email
DECLARE

  en BOOLEAN;
  cc VARCHAR;
  cco VARCHAR;
  tipo VARCHAR;
  brand INTEGER;

BEGIN

  -- Empresa? Ignora
  SELECT "Type"
  INTO tipo
  FROM "Customer"."Customer"
  WHERE id = NEW."Customer_id";
  IF tipo = 'empresa' THEN
    RETURN NULL;
  END IF;

  -- Brand
  SELECT COALESCE(bu."Segment_id", 1)
  INTO brand
  FROM "Booking"."Booking" b
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id"
  WHERE b.id = NEW."Entity_id";

  -- Plantilla
  SELECT "Enabled", "Cc", "Cco"
  INTO en, cc, cco
  FROM "Admin"."Email" e
  LEFT JOIN "Admin"."Email_cc" ec ON e.id = ec."Template_id" AND ec."Segment_id" = brand
  WHERE e."Name" = NEW."Template";

  -- Si existe y esta activa
  IF en = TRUE THEN
    NEW."Cc" = cc;
    NEW."Cco" = cco;
    RETURN NEW;
  END IF;

  -- Ignora el email
  --RAISE NOTICE 'EMAIL % A % IGNORADO', NEW."Template", NEW."Customer_id";
  RETURN NULL;

END;
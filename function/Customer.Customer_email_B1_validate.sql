-- Creación de email
DECLARE

  en BOOLEAN;
  cc VARCHAR;
  cco VARCHAR;
  tipo VARCHAR;
  brand INTEGER;

BEGIN

  -- IPC, send always
  IF NEW."Template" = 'ipc' THEN
    RETURN NEW;
  END IF;

  -- Empresa? Ignora
  SELECT "Type"
  INTO tipo
  FROM "Customer"."Customer"
  WHERE id = NEW."Customer_id";
  IF tipo = 'empresa' THEN
    RETURN NULL;
  END IF;

  -- Brand
  -- La marca la da el piso: las habitaciones y plazas siguen a su piso padre
  SELECT COALESCE(
           CASE WHEN r."Resource_type" = 'piso' THEN r."Segment_id" ELSE f."Segment_id" END,
           1)
  INTO brand
  FROM "Booking"."Booking" b
  INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id"
  LEFT  JOIN "Resource"."Resource" f on f.id = r."Flat_id"
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
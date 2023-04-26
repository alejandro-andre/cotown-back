-- Genera el nº de factura o recibo cuando la factura es definitiva
-- BEFORE INSERT/UPDATE
DECLARE

  format VARCHAR;
  prefix VARCHAR;
  building VARCHAR;
  r_id INTEGER;
  b_id INTEGER;
  n_id INTEGER;
  code VARCHAR;
  num INTEGER;
  yy INTEGER;
  
BEGIN

  RESET ROLE;
  
  -- No se tiene que emitir aún?
  IF NOT NEW."Issued" THEN   
    RETURN NEW;
  END IF;

  -- Ya emitida?
  IF NEW."Code" IS NOT NULL THEN 
    NEW."Issued" := TRUE;
    RETURN NEW;
  END IF;

  -- Lee la info del recurso
  SELECT r.id, r."Code", r."Building_id"
  INTO r_id, code, b_id
  FROM "Resource"."Resource" r
  INNER JOIN "Booking"."Booking" b ON b.id = NEW."Booking_id";

  -- Lee el formato de numeración y prefijo SAP del proveedor
  SELECT
    "Prefix_SAP",
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_pattern" 
      ELSE "Receipt_pattern" 
    END
  INTO prefix, format
  FROM "Provider"."Provider"
  WHERE id = NEW."Provider_id";

  -- Lee el código SAP del edificio
  SELECT "Code_SAP"
  INTO building
  FROM "Building"."Building" b
  WHERE b.id = b_id;

  -- SAP Code
  NEW."SAP_code" := CONCAT(prefix, building, '_', SUBSTRING (code, 8, 5));
  
  -- Año de emisión
  SELECT EXTRACT(YEAR FROM NEW."Issued_date") INTO yy;

  -- Calcula el siguiente número
  SELECT
    id,
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_number" 
      ELSE "Receipt_number" 
    END
  INTO n_id, num
  FROM "Provider"."Provider_bill" pb
  WHERE pb."Provider_id" = NEW."Provider_id" AND "Year" = yy;
  num := 1 + COALESCE(num, 0);

  -- Formatea el número de factura
  SELECT REPLACE (REPLACE (format, '[N]', LPAD(num::TEXT, 5, '0')), '[Y]', yy::text) INTO NEW."Code";

  -- Actualiza el número
  IF n_id IS NULL THEN 
    IF NEW."Bill_type" = 'factura' THEN 
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Receipt_number") VALUES (NEW."Provider_id", yy, 1, 0);
    ELSE
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Receipt_number") VALUES (NEW."Provider_id", yy, 0, 1);
    END IF;
  ELSE
    IF NEW."Bill_type" = 'factura' THEN 
      UPDATE "Provider"."Provider_bill" SET "Bill_number" = num WHERE id = n_id;
    ELSE
      UPDATE "Provider"."Provider_bill" SET "Receipt_number" = num WHERE id = n_id;
    END IF;
  END IF;

  -- Return
  RETURN NEW;

END;
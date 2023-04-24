-- Genera el nº de factura o recibo cuando la factura es definitiva
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
  
  -- Draft
  IF NOT NEW."Issued" THEN   
    RETURN NEW;
  END IF;

  -- Already issued
  IF NEW."Code" IS NOT NULL THEN 
    NEW."Issued" := TRUE;
    RETURN NEW;
  END IF;

  -- Select resource info
  SELECT r.id, r."Code", r."Building_id"
  INTO r_id, code, b_id
  FROM "Resource"."Resource" r
  INNER JOIN "Booking"."Booking" b ON b.id = NEW."Booking_id";

  -- Get provider SAP prefix
  SELECT "Prefix_SAP"
  INTO prefix
  FROM "Provider"."Provider" p
  WHERE p.id = NEW."Provider_id";

  -- Get building SAP code
  SELECT "Code_SAP"
  INTO building
  FROM "Building"."Building" b
  WHERE b.id = b_id;

  -- SAP Code
  NEW."SAP_code" := CONCAT(prefix, building, '_', SUBSTRING (code, 8, 5));
  
  -- Issue year
  SELECT EXTRACT(YEAR FROM NEW."Issued_date") INTO yy;

  -- Get bill code format
  SELECT
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_pattern" 
      ELSE "Receipt_pattern" 
    END
  INTO format
  FROM "Provider"."Provider"
  WHERE id = NEW."Provider_id";

  -- Get next number
  SELECT
    id,
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_number" 
      ELSE "Receipt_number" 
    END
  INTO n_id, num
  FROM "Provider"."Provider_bill" pb
  WHERE pb."Provider_id" = NEW."Provider_id" AND "Year" = yy;

  -- Next num
  num := 1 + COALESCE(num, 0);

  -- Invoice number format
  SELECT REPLACE (REPLACE (format, '[N]', LPAD(num::TEXT, 5, '0')), '[Y]', yy::text) INTO NEW."Code";

  -- Update number
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

  -- Return code
  RETURN NEW;

END;
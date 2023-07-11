-- Genera el nº de factura o recibo cuando la factura es definitiva
-- BEFORE INSERT/UPDATE
DECLARE

  customer_id INTEGER;
  prefix_provider VARCHAR;
  prefix_building VARCHAR;
  format VARCHAR;

  booking_id INTEGER;
  resource_id INTEGER;
  building_id INTEGER;
  resource_code VARCHAR;

  i_id INTEGER;
  n_id INTEGER;
  num INTEGER;
  yy INTEGER;
  
  reg RECORD;
  lines CURSOR FOR 
    SELECT *
    FROM "Billing"."Invoice_line"
    WHERE "Invoice_id" = NEW.id;
   
BEGIN

  -- Cliente de la reserva
  IF NEW."Customer_id" IS NULL THEN
    IF NEW."Booking_id" IS NOT NULL THEN
      SELECT "Customer_id" INTO customer_id FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
      NEW."Customer_id" := customer_id;
    ELSE
      IF NEW."Booking_group_id" IS NOT NULL THEN
        SELECT "Customer_id" INTO customer_id FROM "Booking"."Booking_group" WHERE id = NEW."Booking_group_id";
        NEW."Customer_id" := customer_id;
      ELSE
        RAISE EXCEPTION '!!!Client is missing!!!Falta indicar el cliente!!!';
      END IF;
    END IF;
  END IF;

  -- No se tiene que emitir aún?
  IF NOT NEW."Issued" AND NEW."Code" IS NULL THEN   
    RETURN NEW;
  END IF;
  NEW."Issued" := TRUE;

  -- No se puede cambiar
  IF OLD."Issued" = TRUE THEN
    NEW."Issued" = TRUE;
  END IF;
  IF OLD."Rectified" = TRUE THEN
    NEW."Rectified" = TRUE;
  END IF;

  -- Ya emitida?
  IF NEW."Issued" = TRUE AND NEW."Code" IS NOT NULL THEN

    -- Rectificativa?
    IF NEW."Bill_type" = 'factura' AND OLD."Rectified" = FALSE AND NEW."Rectified" = TRUE  THEN

      -- Inserta factura rectificativa
 	    INSERT INTO "Billing"."Invoice" 
        ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
      VALUES 
        ('rectificativa', False, False, CURRENT_DATE, OLD."Provider_id", OLD."Customer_id", OLD."Booking_id", OLD."Payment_method_id", OLD."Payment_id", CONCAT('Factura rectificativa de la ', OLD."Code"))
      RETURNING id INTO i_id;
     
      -- Inserta lineas
      OPEN lines;
      FETCH lines INTO reg;
      WHILE (FOUND) LOOP
        INSERT INTO "Billing"."Invoice_line" 
          ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept") 
        VALUES
          (i_id, -reg."Amount", reg."Product_id", reg."Tax_id", reg."Concept");
        FETCH lines INTO reg;
      END LOOP;     
      CLOSE lines;

      -- Emite factura
 	    UPDATE "Billing"."Invoice" SET "Issued" = TRUE WHERE id = i_id;
      RETURN NEW;
 	  
    END IF;
   
    -- No permite cambios
    IF OLD."Bill_type" <> NEW."Bill_type"
    OR OLD."Booking_group_id" <> NEW."Booking_group_id"
    OR OLD."Booking_id" <> NEW."Booking_id"
    OR OLD."Concept" <> NEW."Concept"
    OR OLD."Customer_id" <> NEW."Customer_id"
    OR OLD."Issued_date" <> NEW."Issued_date"
    OR OLD."Provider_id" <> NEW."Provider_id" THEN
      RAISE EXCEPTION '!!!Bill has been already issued, cannot change!!!La factura ya ha sido emitida, no puede cambiarse!!!'; 
    END IF;
    RETURN NEW;
   
  END IF;

  -- Lee la info del recurso
  booking_id := NEW."Booking_id";
  IF booking_id IS NULL THEN
    booking_id := NEW."Booking_group_id";
  END IF;
  SELECT r.id, r."Code", r."Building_id"
  INTO resource_id, resource_code, building_id
  FROM "Resource"."Resource" r
  INNER JOIN "Booking"."Booking" b ON b.id = booking_id;

  -- Lee el formato de numeración y prefijo SAP del proveedor
  SELECT
    "Prefix_SAP",
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_pattern" 
      WHEN 'rectificativa' THEN "Credit_pattern" 
      ELSE "Receipt_pattern" 
    END
  INTO prefix_provider, format
  FROM "Provider"."Provider"
  WHERE id = NEW."Provider_id";

  -- Lee el código SAP del edificio
  SELECT "Code_SAP"
  INTO prefix_building
  FROM "Building"."Building" b
  WHERE b.id = building_id;

  -- SAP Code
  NEW."SAP_code" := CONCAT(prefix_provider, prefix_building, '_', SUBSTRING (resource_code, 8, 5));
  
  -- Año de emisión
  SELECT EXTRACT(YEAR FROM NEW."Issued_date") INTO yy;

  -- Calcula el siguiente número
  SELECT
    id,
    CASE NEW."Bill_type"
      WHEN 'factura' THEN "Bill_number" 
      WHEN 'rectificativa' THEN "Credit_number" 
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
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number") VALUES (NEW."Provider_id", yy, 1, 0, 0);
    END IF;
    IF NEW."Bill_type" = 'rectificativa' THEN 
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number") VALUES (NEW."Provider_id", yy, 0, 1, 0);
    END IF;
    IF NEW."Bill_type" = 'recibo' THEN 
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number") VALUES (NEW."Provider_id", yy, 0, 0, 1);
    END IF;
  ELSE
    IF NEW."Bill_type" = 'factura' THEN 
      UPDATE "Provider"."Provider_bill" SET "Bill_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'rectificativa' THEN 
      UPDATE "Provider"."Provider_bill" SET "Credit_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'recibo' THEN 
      UPDATE "Provider"."Provider_bill" SET "Receipt_number" = num WHERE id = n_id;
    END IF;
  END IF;

  -- Return
  RETURN NEW;

END;

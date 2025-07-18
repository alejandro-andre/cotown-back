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
 
  total NUMERIC;
 
  reg RECORD;
  lines CURSOR FOR
    SELECT *
    FROM "Billing"."Invoice_line"
    WHERE "Invoice_id" = NEW.id;
  
BEGIN

  -- Delete
  IF TG_OP = 'DELETE' THEN
    IF OLD."Issued" = FALSE OR current_setting('myapp.admin', true) = 'true' THEN
      RETURN OLD;
    END IF;    
    RAISE EXCEPTION '!!!Cannot delete issued bill!!!No se puede borrar una factura emitida!!!';
  END IF;

  -- Update, and already issued
  IF OLD."Issued" = TRUE THEN

    -- Rectificativa?
    IF NEW."Bill_type" = 'factura' AND OLD."Rectified" = FALSE AND NEW."Rectified" = TRUE THEN

      -- Inserta factura rectificativa
	    INSERT INTO "Billing"."Invoice"
        ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Booking_group_id", "Booking_other_id", "Payment_method_id", "Payment_id", "Concept")
      VALUES
        ('rectificativa', False, False, CURRENT_DATE, OLD."Provider_id", OLD."Customer_id", OLD."Booking_id", OLD."Booking_group_id", OLD."Booking_other_id", OLD."Payment_method_id", OLD."Payment_id", CONCAT('Factura rectificativa de la ', OLD."Code"))
      RETURNING id INTO i_id;
    
      -- Inserta lineas
      OPEN lines;
      FETCH lines INTO reg;
      WHILE (FOUND) LOOP
        INSERT INTO "Billing"."Invoice_line"
          ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept", "Resource_id")
        VALUES
          (i_id, -reg."Amount", reg."Product_id", reg."Tax_id", reg."Concept", reg."Resource_id");
        FETCH lines INTO reg;
      END LOOP;    
      CLOSE lines;

      -- Emite factura
	    UPDATE "Billing"."Invoice" SET "Issued" = TRUE, "Issued_date" = CURRENT_DATE WHERE id = i_id;
      RETURN NEW;
     
    END IF;

    -- No se puede cambiar
    IF OLD."Issued"            <> NEW."Issued"           OR
       OLD."Bill_type"         <> NEW."Bill_type"        OR
       OLD."Booking_id"        <> NEW."Booking_id"       OR
       OLD."Booking_group_id"  <> NEW."Booking_group_id" OR
       OLD."Customer_id"       <> NEW."Customer_id"      OR
       OLD."Provider_id"       <> NEW."Provider_id"      OR
       OLD."Concept"           <> NEW."Concept"          OR
       OLD."Issued_date"       <> NEW."Issued_date"      OR
      (OLD."Rectified" = TRUE AND NEW."Rectified" = FALSE) THEN
      IF CURRENT_USER <> 'modelsadmin'AND current_setting('myapp.admin', true) <> 'true' THEN
        RAISE EXCEPTION '!!!Cannot change issued bill!!!No se puede cambiar una factura emitida!!!';
      END IF;
      RETURN NEW;
    END IF;

  END IF;

  -- Campos obligatorios
  IF NEW."Bill_type" IS NULL THEN
    RAISE EXCEPTION '!!!Type field is mandatory!!!El campo tipo es obligatorio!!!';
  END IF;
  IF NEW."Payment_method_id" IS NULL THEN
    RAISE EXCEPTION '!!!Payment method field is mandatory!!!El campo medio de pago es obligatorio!!!';
  END IF;
  IF NEW."Provider_id" IS NULL THEN
    RAISE EXCEPTION '!!!Issuer field is mandatory!!!El campo emisor es obligatorio!!!';
  END IF;
  IF NEW."Concept" IS NULL THEN
    RAISE EXCEPTION '!!!Concept field is mandatory!!!El campo concepto es obligatorio!!!';
  END IF;
  IF NEW."Booking_id" IS NULL AND NEW."Booking_group_id" IS NULL AND NEW."Booking_other_id" IS NULL THEN
    RAISE EXCEPTION '!!!B2C, B2B or other booking is missing!!!Falta indicar la reserva B2C, B2B u otra!!!';
  END IF;

  -- Cliente
  IF NEW."Booking_id" IS NOT NULL THEN
    SELECT "Customer_id" INTO customer_id FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
    NEW."Customer_id" := customer_id;
  ELSE
    IF NEW."Booking_group_id" IS NOT NULL THEN
      SELECT "Payer_id" INTO customer_id FROM "Booking"."Booking_group" WHERE id = NEW."Booking_group_id";
      NEW."Customer_id" := customer_id;
    ELSE
      IF NEW."Booking_other_id" IS NOT NULL THEN
        SELECT "Customer_id" INTO customer_id FROM "Booking"."Booking_other" WHERE id = NEW."Booking_other_id";
        NEW."Customer_id" := customer_id;
      ELSE
        RAISE EXCEPTION '!!!Client is missing!!!Falta indicar el cliente!!!';
      END IF;
    END IF;
  END IF;

  -- No se tiene que emitir aún?
  IF NOT NEW."Issued" THEN  
    RETURN NEW;
  END IF;

  -- Emitida anteriormente
  IF OLD."Code" IS NOT NULL THEN  
    RETURN NEW;
  END IF;

  -- Validate amount
  SELECT SUM("Amount")
  INTO total
  FROM "Billing"."Invoice_line"
  WHERE "Invoice_id" = NEW.id;
  IF NEW."Bill_type" <> 'rectificativa' THEN
    IF total IS NULL OR total <= 0 THEN
      RAISE EXCEPTION '!!!Invoice with amount less or equal to 0!!!Factura con importe menor o igual a 0!!!';
    END IF;
  ELSE
    IF total IS NULL OR total >= 0 THEN
      RAISE EXCEPTION '!!!Invoice with amount greater or equal to 0!!!Factura rectificativa con importe mayor o igual a 0!!!';
    END IF;
  END IF;

  -- Lee el formato de numeración del proveedor
  SELECT
    CASE
      WHEN  NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NULL THEN "Bill_pattern"
      WHEN  NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NOT NULL THEN "LAU_bill_pattern"
      WHEN  NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NULL THEN "Credit_pattern"
      WHEN  NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NOT NULL THEN "LAU_credit_pattern"
      ELSE "Receipt_pattern"
    END
  INTO format
  FROM "Provider"."Provider"
  WHERE id = NEW."Provider_id";

  -- Fecha y año de emisión
  NEW."Issued_date" := CURRENT_DATE;
  SELECT EXTRACT(YEAR FROM NEW."Issued_date") INTO yy;

  -- Calcula el siguiente número
  SELECT
    id,
    CASE
      WHEN  NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NULL THEN "Bill_number"
      WHEN  NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NOT NULL THEN "LAU_bill_number"
      WHEN  NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NULL THEN "Credit_number"
      WHEN  NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NOT NULL THEN "LAU_credit_number"
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
    IF NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NULL THEN
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number", "LAU_bill_number", "LAU_credit_number") VALUES (NEW."Provider_id", yy, 1, 0, 0, 0, 0);
    END IF;
    IF NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NULL THEN
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number", "LAU_bill_number", "LAU_credit_number") VALUES (NEW."Provider_id", yy, 0, 1, 0, 0, 0);
    END IF;
    IF NEW."Bill_type" = 'recibo' THEN
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number", "LAU_bill_number", "LAU_credit_number") VALUES (NEW."Provider_id", yy, 0, 0, 1, 0, 0);
    END IF;
    IF NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NOT NULL THEN
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number", "LAU_bill_number", "LAU_credit_number") VALUES (NEW."Provider_id", yy, 0, 0, 0, 1, 0);
    END IF;
    IF NEW."Bill_type" = 'rectificativa' AND NEW."Booking_other_id" IS NOT NULL THEN
      INSERT INTO "Provider"."Provider_bill" ("Provider_id", "Year", "Bill_number", "Credit_number", "Receipt_number", "LAU_bill_number", "LAU_credit_number") VALUES (NEW."Provider_id", yy, 0, 0, 0, 0, 1);
    END IF;
  ELSE
    IF NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NULL THEN
      UPDATE "Provider"."Provider_bill" SET "Bill_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'rectificativa'AND NEW."Booking_other_id" IS NULL THEN
      UPDATE "Provider"."Provider_bill" SET "Credit_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'recibo' THEN
      UPDATE "Provider"."Provider_bill" SET "Receipt_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'factura' AND NEW."Booking_other_id" IS NOT NULL THEN
      UPDATE "Provider"."Provider_bill" SET "LAU_bill_number" = num WHERE id = n_id;
    END IF;
    IF NEW."Bill_type" = 'rectificativa'AND NEW."Booking_other_id" IS NOT NULL THEN
      UPDATE "Provider"."Provider_bill" SET "LAU_credit_number" = num WHERE id = n_id;
    END IF;
  END IF;

  -- Return
  RETURN NEW;

END;

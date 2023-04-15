DECLARE

  invoice_id INTEGER;
  customer_id INTEGER;
  status_record VARCHAR;
  y VARCHAR;

BEGIN

  -- Asigna el link del boton para el pago por TPV
  IF (NEW."Payment_method_id" = 1 AND NEW."Payment_date" IS NULL) THEN
    NEW."Pay" := CONCAT('/functions/Auxiliar.goin?url=/admin/Billing.Pay/external?id=', NEW.id);
    RETURN NEW;
  END IF;

  -- Comprobamos si el pago se ha llevado a cabo correctamente 
  IF (NEW."Payment_date" IS NULL) THEN 
    RETURN NEW;
  END IF;

  -- Pago manual (sin auth code)
  IF (NEW."Payment_auth" IS NULL) THEN
	  SELECT to_char(now(), 'YY') INTO y;
    NEW."Payment_order" := CONCAT(y, LPAD(NEW.id::text, 5, '0'), '00000');
    NEW."Payment_auth" := 'MANUAL';
  END IF;

  -- Pago realizado, quita el botón
  NEW."Pay" := NULL;

  -- Seleccionamos el estado actual de la reserva
  SELECT "Status" INTO status_record FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
  
  -- Comprobamos si el tipo de pago es 'booking'
  IF (NEW."Payment_type" = 'booking') THEN

    -- Registra el pago
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Booking fee pagado');

    -- Crea la factura - Pasar al proceso de facturación
    -- SELECT "Customer_id" INTO customer_id FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
    -- INSERT INTO "Billing"."Invoice" 
    --   ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Details", "Payment_method_id", "Payment_id") 
    --   VALUES ('factura', TRUE, CURRENT_DATE, 1, customer_id, NEW."Booking_id", 'Booking fee', NEW."Payment_method_id", NEW.id)
    --   RETURNING id INTO invoice_id;
    -- INSERT INTO "Billing"."Invoice_line" ("Invoice_id", "Product_id", "Amount", "Tax_id", "Details") VALUES (invoice_id, 1, NEW."Amount", 1, 'Booking fee');

    -- Comprobamos si el estado es 'solicitud'
    IF (status_record = 'solicitud') THEN
      UPDATE "Booking"."Booking" SET "Status" ='solicitudpagada' WHERE id = NEW."Booking_id";
      RETURN NEW;
    END IF;
  
    -- Comprobamos si el estado es 'alternativas'
    IF (status_record = 'alternativas') THEN
      UPDATE "Booking"."Booking" SET "Status" ='alternativaspagada' WHERE id = NEW."Booking_id";
      RETURN NEW;
    END IF;
  
    -- Comprobamos si el estado es 'pendientepago'
    IF (status_record = 'pendientepago') THEN
      UPDATE "Booking"."Booking" SET "Status" ='confirmada' WHERE id = NEW."Booking_id";
      RETURN NEW;
    END IF;    

  END IF;

  -- Comprobamos si el tipo de pago es 'deposito'
  IF (NEW."Payment_type" = 'deposito') THEN

    -- Registra el pago
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Garantía pagada');

    IF (status_record = 'confirmada') THEN
      UPDATE "Booking"."Booking" SET "Status" ='firmacontrato' WHERE id=NEW."Booking_id";
      RETURN NEW;
    END IF;

  END IF;

  RETURN NEW;

END;

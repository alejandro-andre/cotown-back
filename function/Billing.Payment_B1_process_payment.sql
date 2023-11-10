-- Procesa los pagos
DECLARE

  invoice_id INTEGER;
  customer_id INTEGER;
  status_record VARCHAR;
  deposit NUMERIC;
  y VARCHAR;
  curr_user VARCHAR;

BEGIN

  -- Asigna el link del boton para el pago por TPV
  --IF (NEW."Payment_method_id" = 1 AND NEW."Payment_date" IS NULL) THEN
  --  NEW."Pay" := CONCAT('/functions/Admin.goin?url=/admin/Billing.Pay/external?id=', NEW.id);
  --  RETURN NEW;
  --END IF;

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
  SELECT "Status", "Deposit" INTO status_record, deposit FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
 
  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Comprobamos si el tipo de pago es 'booking'
  IF (NEW."Payment_type" = 'booking') THEN

    -- Registra el pago
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Booking fee pagado');

    -- SOLICITUD a SOLICITUD PAGADA
    -- Comprobamos si el estado es 'solicitud'
    IF (status_record = 'solicitud') THEN
      UPDATE "Booking"."Booking" SET "Status" ='solicitudpagada', "Booking_fee_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
    END IF;
 
    -- ALTERNATIVAS a ALTERNATIVAS PAGADA
    -- Comprobamos si el estado es 'alternativas'
    IF (status_record = 'alternativas') THEN
      UPDATE "Booking"."Booking" SET "Status" ='alternativaspagada', "Booking_fee_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
    END IF;
 
    -- PENDIENTE PAGO a CONFIRMADA o FIRMACONTRATO
    -- Comprobamos si el estado es 'pendientepago'
    IF (status_record = 'pendientepago') THEN

      -- Deposito no pagado aun
      IF deposit IS NULL THEN
        UPDATE "Booking"."Booking" SET "Status" ='confirmada', "Booking_fee_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
      -- Deposito pagado ANTES QUE EL BOOKING FEE
      ELSE
        UPDATE "Booking"."Booking" SET "Status" ='firmacontrato', "Booking_fee_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
      END IF;
     
    END IF;   

  END IF;

  -- Comprobamos si el tipo de pago es 'deposito'
  IF (NEW."Payment_type" = 'deposito') THEN

    -- Registra el pago
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Garantía pagada');

    -- CONFIRMADA a FIRMA CONTRATO
    IF (status_record = 'confirmada') OR (NEW."Booking_fee_actual" IS NOT NULL) THEN
      UPDATE "Booking"."Booking" SET "Status" ='firmacontrato', "Deposit_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
    ELSE
      UPDATE "Booking"."Booking" SET "Deposit_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
    END IF;

  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
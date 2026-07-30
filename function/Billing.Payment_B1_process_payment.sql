-- Procesa los pagos
DECLARE

  invoice_id INTEGER;
  customer_id INTEGER;
  status_record VARCHAR;
  deposit NUMERIC;
  deposit_actual NUMERIC;
  booking_fee NUMERIC;
  booking_fee_actual NUMERIC;
  y VARCHAR;
  curr_user VARCHAR;
  err TEXT;
  err_state TEXT;

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

  -- Importe pagado
  IF NEW."Amount_payed" IS NULL THEN
    NEW."Amount_payed" := NEW."Amount";
  END IF;

  -- Ya pagado?
  IF OLD."Payment_date" IS NOT NULL THEN
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

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Sub transaccion
  BEGIN

    -- Seleccionamos el estado actual de la reserva
    SELECT "Status", "Deposit", "Deposit_actual", "Booking_fee", "Booking_fee_actual"
    INTO status_record, deposit, deposit_actual, booking_fee, booking_fee_actual
    FROM "Booking"."Booking" WHERE id = NEW."Booking_id";

    -- Comprobamos si el tipo de pago es 'booking' B2C
    IF (NEW."Payment_type" = 'booking' AND NEW."Booking_id" IS NOT NULL) THEN

      -- Registra el pago
      INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Membership fee pagado');

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
        UPDATE "Booking"."Booking" SET "Status" ='confirmada', "Booking_fee_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
      END IF;

    END IF;

    -- Comprobamos si el tipo de pago es 'deposito'
    IF (NEW."Payment_type" = 'deposito' AND NEW."Booking_id" IS NOT NULL) THEN

      -- Registra el pago
      INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Garantía pagada');

      -- DOCUMENTACION OK a FIRMA CONTRATO
      IF status_record = 'documentacionok' OR booking_fee = 0 OR booking_fee_actual IS NOT NULL THEN
        UPDATE "Booking"."Booking" SET "Status" ='firmacontrato', "Deposit_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
      ELSE
        UPDATE "Booking"."Booking" SET "Deposit_actual" = NEW."Amount" WHERE id = NEW."Booking_id";
      END IF;

    END IF;

  -- El pago se registra igualmente, sólo se anota el fallo del workflow
  EXCEPTION WHEN OTHERS THEN

    -- Anota el error en la reserva (sin poder tumbar el registro del pago)
    IF NEW."Booking_id" IS NOT NULL THEN
      BEGIN
        INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log")
        VALUES (NEW."Booking_id", CONCAT('ERROR: pago ', NEW.id, ' (', NEW."Payment_type", ', ', NEW."Amount", ') cobrado y registrado, pero NO se ha podido actualizar la reserva: ', err));
        EXCEPTION WHEN OTHERS THEN NULL;
      END;
    END IF;

  END;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
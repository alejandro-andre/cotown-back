-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;
  record_id INTEGER = 0;
  payment_method_id INTEGER = 1;
  curr_user VARCHAR;
  deposit BOOLEAN = FALSE;
  num INTEGER;
  pos "Auxiliar"."Pos_type";

BEGIN

  -- Customer payment method
  SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";

  -- Por defecto, deshabilita el botón de envío de alternativas
  NEW."Button_options" := '';
  IF NEW."Status" = 'solicitud' THEN
    IF (SELECT COUNT(*) FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW.id AND "Accepted" = TRUE) = 0 AND
       (SELECT COUNT(*) FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW.id AND "Accepted" = FALSE) > 0 THEN
      NEW."Button_options" := CONCAT('https://back.cotown.com/api/v1/booking/', NEW.id, '/status/alternativas');
    END IF;
  END IF;
  IF NEW."Status" = 'solicitudpagada' THEN
    IF (SELECT COUNT(*) FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW.id AND "Accepted" = TRUE) = 0 AND
       (SELECT COUNT(*) FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW.id AND "Accepted" = FALSE) > 0 THEN
      NEW."Button_options" := CONCAT('https://back.cotown.com/api/v1/booking/', NEW.id, '/status/alternativaspagada');
    END IF;
  END IF;

  -- Membership fee check
  --IF COALESCE(NEW."Booking_fee", 0) <> COALESCE(NEW."Booking_fee_calc", 0) AND NEW."Booking_discount_type_id" IS NULL THEN
  --  RAISE EXCEPTION '!!!Discount reason is mandatory!!!Es obligatorio indicar motivo de descuento!!!';
  --END IF;

  -- Update membership fee
  IF OLD."Booking_fee" <> NEW."Booking_fee" OR (OLD."Booking_fee" IS NULL AND NEW."Booking_fee" > 0) THEN

    -- Already paid?
    SELECT COUNT(*) INTO num 
    FROM "Billing"."Payment" 
    WHERE "Payment_type" = 'booking'
      AND "Customer_id" = NEW."Customer_id" 
      AND "Booking_id" = NEW.id
      AND "Payment_date" IS NOT NULL;
    IF num > 0 THEN
      RAISE WARNING '!!!Mambership fee already paid!!!El Mambership fee ya ha sido pagado!!!';

    -- Update fee (delete + update)
    ELSE
      curr_user := CURRENT_USER;
      RESET ROLE;
      DELETE FROM "Billing"."Payment" WHERE "Payment_type" = 'booking' AND "Customer_id" = NEW."Customer_id" AND "Booking_id" = NEW.id;
      IF NEW."Booking_fee" > 0 THEN
        SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";
        INSERT
          INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (COALESCE(payment_method_id, 1), 'cotown', NEW."Customer_id", NEW.id, NEW."Booking_fee", CURRENT_DATE, 'Membership fee', 'booking');
      END IF;
      EXECUTE 'SET ROLE "' || curr_user || '"';
    END IF;
    
  END IF;

  -- Update deposit
  IF COALESCE(OLD."Deposit", 0) <> COALESCE(NEW."Deposit", 0) THEN

    -- Already paid?
    SELECT COUNT(*) INTO num 
    FROM "Billing"."Payment" 
    WHERE "Payment_type" = 'deposito'
      AND "Customer_id" = NEW."Customer_id" 
      AND "Booking_id" = NEW.id
      AND "Payment_date" IS NOT NULL;
    IF num > 0 THEN
      RAISE WARNING '!!!Deposit already paid!!!La garantía ya ha sido pagada!!!';

    -- Update deposit (delete + update)
    ELSE
      curr_user := CURRENT_USER;
      RESET ROLE;
      DELETE FROM "Billing"."Payment" WHERE "Payment_type" = 'deposito' AND "Customer_id" = NEW."Customer_id" AND "Booking_id" = NEW.id;
      -- Deposit is 0
      IF NEW."Deposit" = 0 AND COALESCE(NEW."Deposit_actual", 0) = 0 THEN
        NEW."Deposit_actual" = 0;
      END IF;
      -- Add payment if actual deposit is 0
      IF NEW."Deposit" > 0 AND COALESCE(NEW."Deposit_actual", 0) = 0 THEN
        SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";
        SELECT p."Pos" INTO pos FROM "Resource"."Resource" r LEFT JOIN "Provider"."Provider" p ON p.id = r."Owner_id" WHERE r.id = NEW."Resource_id";
        INSERT
          INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (COALESCE(payment_method_id, 1), pos, NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Garantía', 'deposito');
      END IF;
      EXECUTE 'SET ROLE "' || curr_user || '"';
    END IF;
    
  END IF;

  -- SOLICITUD a PENDIENTE DE PAGO
  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso a una solicitud no pagada
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" :='pendientepago';
    deposit := TRUE;
  END IF;

  -- PENDIENTE DE PAGO A CADUCADA
  -- Actualiza al estado 'caducada'
  IF (NEW."Status" = 'pendientepago' AND NEW."Expiry_date" < CURRENT_DATE)  THEN
    NEW."Status" :='caducada';
  END IF;

  -- CADUCADA A PENDIENTE DE PAGO
  -- Actualiza al estado 'Pendiente de pago'
  IF (NEW."Status" = 'caducada' AND NEW."Expiry_date" >= CURRENT_DATE)  THEN
    NEW."Status" :='pendientepago';
  END IF;

  -- SOLICITUD PAGADA o ALTERNATIVA PAGADA a CONFIRMADA
  -- Actualiza al estado 'Confirmada' cuando se asigna el recurso a una solicitud pagada
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN
    -- Si hay que pagar garantía, pasa a confirmada
    IF NEW."Deposit" > 0 AND NEW."Deposit_actual" IS NULL THEN
      NEW."Status" := 'confirmada';
      deposit := TRUE;
    -- Si no hay que pagar garantía o ya está pagada, pasa a firma contrato
    ELSE
      NEW."Status" := 'firmacontrato';
    END IF;
  END IF;

  -- FIRMA CONTRATO a CONTRATO
  -- Actualiza el estado a "contrato" desde 'firmacontrato' cuando firma el contrado (Fecha contract_signed rellena)
  IF (NEW."Status" = 'firmacontrato' AND NEW."Contract_signed" IS NOT NULL) THEN
    NEW."Status" := 'contrato';
  END IF;

  -- CONTRATO a FIRMACONTRATO
  -- Actualiza el estado a "firmacontrato" cuando se quita la firma, tiene que firmarse el contrato nuevamente
  IF (NEW."Status" = 'contrato' AND (NEW."Contract_signed" IS NULL OR NEW."Contract_rent" IS NULL)) THEN
    NEW."Status" := 'firmacontrato';
    NEW."Contract_signed" := NULL;
  END IF;
 
  -- CONTRATO a CHECK IN CONFIRMADO
  -- Actualiza al estado 'Checkin confirmado' cuando se asigna la fecha de checkin
  IF (NEW."Status" = 'contrato' AND NEW."Check_in" IS NOT NULL) THEN
    NEW."Status" := 'checkinconfirmado';
  END IF;

  -- CHECK IN A CONTRATO o CHECK IN CONFIRMADO
  -- Actualiza al estado cuando se aplaza el checkin
  IF (NEW."Status" = 'checkin' AND COALESCE(NEW."Check_in", NEW."Date_from") > CURRENT_DATE) THEN
    IF NEW."Check_in" IS NULL THEN
      NEW."Status" := 'contrato';
    ELSE
      NEW."Status" := 'checkinconfirmado';
    END IF;
  END IF;

  -- DESCARTADA PAGADA a DESCARTADA
  -- Actualiza el estado a "descartada" cuando se devuelve el membership fee
  IF (NEW."Status" = 'descartadapagada' AND NEW."Booking_fee_returned" IS NOT NULL) THEN
    NEW."Status" := 'descartada';
  END IF;

  -- REVISION a DEVOLVER GARANTIA
  -- Actualiza el estado a "devolver garantía" cuando se confirma la revisión
  IF (NEW."Status" = 'revision' AND NEW."Check_out_revision_ok") THEN
    NEW."Status" := 'devolvergarantia';
  END IF;

  -- DEVOLVER GARANTIA a FINALIZADA
  -- Actualiza el estado a "finalizada" cuando se devuelve la garantía
  IF (NEW."Status" = 'devolvergarantia' AND NEW."Deposit_returned" IS NOT NULL) THEN
    NEW."Status" := 'finalizada';
  END IF;

  -- CONTRATO GENERADO
  -- Envia mail contrato
  IF (OLD."Contract_rent" IS NULL AND NOT NEW."Contract_rent" IS NULL) THEN
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'firmacontrato', NEW.id);
  END IF;

  -- No ha habido cambios de estado
  IF (NEW."Status" = OLD."Status" AND OLD."Resource_id" = NEW."Resource_id") THEN
    RETURN NEW;
  END IF;

  -- ######################################################
  -- Procesa los cambios
  -- ######################################################

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Depósito
  IF deposit THEN
    IF NEW."Deposit" > 0 AND NEW."Deposit_actual" IS NULL THEN
      DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW."id" AND "Payment_date" IS NULL and "Payment_type" = 'deposito' ;
      IF NEW."Deposit" > 0 AND NEW."Deposit_actual" IS NULL THEN
        SELECT p."Pos" INTO pos FROM "Resource"."Resource" r LEFT JOIN "Provider"."Provider" p ON p.id = r."Owner_id" WHERE r.id = NEW."Resource_id";
        INSERT
          INTO "Billing"."Payment" ("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) 
          VALUES (COALESCE(payment_method_id, 1), pos, NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Garantía', 'deposito');
      END IF;
    END IF;
  END IF;

  -- A ALTERNATIVA o ALTERNATIVAS PAGADA
  IF (NEW."Status" = 'alternativas' OR NEW."Status" = 'alternativaspagada') THEN
    -- Email
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'alternativas', NEW.id);
    -- Log
    change := 'Revisar alternativas';
  END IF;

  -- A PENDIENTE DE PAGO
  IF (NEW."Status" = 'pendientepago' ) THEN
    -- Actualiza la fecha de expiracion
    IF (NEW."Expiry_date" IS NULL) THEN
      NEW."Expiry_date" := (CURRENT_DATE + INTERVAL '2 days');
    ELSE
      IF (NEW."Expiry_date" < (CURRENT_DATE + INTERVAL '2 days')) THEN
        NEW."Expiry_date" := (CURRENT_DATE + INTERVAL '2 days');
      END IF;
    END IF;
    -- Email
    IF NEW."Origin_id" IS NULL THEN
      INSERT
        INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
        VALUES (NEW."Customer_id", 'pendientepago', NEW.id);
    END IF;
    -- Log
    change := 'Pendiente de pago';
  END IF;

  -- A CADUCADA
	IF (NEW."Status" = 'caducada') THEN
		-- Envia email informando de la caducidad
		INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'caducada', NEW.id);
		-- Log
		change := CONCAT('La solicitud ha caducado el día ', NEW."Expiry_date");
	END IF;

  -- A CONFIRMADA
  IF (NEW."Status" = 'confirmada') THEN
    -- Confirmada
    IF NEW."Confirmation_date" IS NULL THEN
      NEW."Confirmation_date" := CURRENT_DATE;
    END IF;
    NEW."Expiry_date" := NULL;
    -- Borramos las alternativas asociadas a la solicitud
    DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."id";
    -- EMail
    IF NEW."Origin_id" IS NULL THEN
      INSERT
        INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
        VALUES (NEW."Customer_id", 'confirmada', NEW.id);
    END IF;
    -- Log
    change := 'Reserva confirmada';
  END IF;

  -- A DESCARTADA PAGADA
  IF (NEW."Status" = 'descartadapagada') THEN
    -- Quita el recurso
    NEW."Resource_id" := NULL;
    -- EMail
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'descartadapagada', NEW.id);
    -- Log
    change := 'Solicitud descartada y booking pagado.';  
  END IF;

  -- A DESCARTADA
  IF (NEW."Status" = 'descartada' OR NEW."Status" = 'descartadapagada') THEN
    -- Quita el recurso
    NEW."Resource_id" := NULL;
    -- Intentamos eliminar pagos no realizados
    BEGIN
      DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id AND "Payment_date" IS NULL;
      EXCEPTION WHEN OTHERS THEN NULL;
    END;
    -- EMail
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", NEW."Status", NEW.id);
    -- Log
    change := 'Solicitud descartada.';
    IF (NEW."Booking_fee_returned" IS NOT NULL) THEN
      change := CONCAT(change, ' Hay que devolver el booking con por importe de: ', NEW."Booking_fee_returned");
    END IF;
  END IF;

  -- A FIRMA CONTRATO
  IF (NEW."Status" = 'firmacontrato') THEN
    -- Confirmada
    IF NEW."Confirmation_date" IS NULL THEN
      NEW."Confirmation_date" := CURRENT_DATE;
    END IF;
    NEW."Expiry_date" := NULL;
    -- Log
    change := 'Pendiente de firmar el contrato de la reserva';
  END IF;

  -- A CONTRATO
  IF (NEW."Status" = 'contrato') THEN
    -- EMail
    --?IF NEW."Check_in" IS NULL AND NEW."Origin_id" IS NULL THEN
    --?  INSERT
    --?    INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
    --?    VALUES (NEW."Customer_id", 'completacheckin', NEW.id);
    --?END IF;
    -- Log
    change := CONCAT('Firmado contrato de la reserva ', NEW."Contract_signed");
  END IF;

  -- A CHECK IN CONFIRMADO
  IF (NEW."Status" = 'checkinconfirmado' OR (NEW."Status" = 'checkin' AND OLD."Status" = 'contrato')) THEN
    -- Email
    IF NEW."Origin_id" IS NULL THEN
      INSERT
        INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
        VALUES (NEW."Customer_id", 'checkinconfirmado', NEW.id);
    END IF;
    -- Log
    change := CONCAT('Confirmada la fecha de checkin de la reserva ', NEW."Check_in");
  END IF;


  -- A CANCELADA
  -- Intentamos eliminar pagos no realizados
  IF (NEW."Status" = 'cancelada') THEN
    BEGIN
      DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id AND "Payment_date" IS NULL;
      EXCEPTION WHEN OTHERS THEN NULL;
    END;
  END IF;

  -- A IN HOUSE (BOTON 'CHECK IN OK')
  -- Se confirma la llegada del usuario al alojamiento
  IF (NEW."Status" = 'inhouse') THEN 
    IF NEW."Origin_id" IS NULL THEN
      -- Questionnaire
      INSERT
        INTO "Booking"."Booking_questionnaire" ("Booking_id", "Questionnaire_type")
        VALUES (NEW.id, 'checkin');
      -- EMail
      INSERT
        INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
        VALUES (NEW."Customer_id", 'inhouse', NEW.id);
    END IF;
    -- Log
    change := 'Se confirma que el usuario ha llegado al alojamiento.';  
  END IF;

  -- A DEVOLVER GARANTIA
  -- Se confirma que el usuario abandona el alojamiento en perfectas condiciones
  IF (NEW."Status" = 'devolvergarantia') THEN
    -- EMail
    INSERT 
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      VALUES (NEW."Customer_id", 'devolvergarantia', NEW.id);
    -- Log
    change := CONCAT('El checkout ha sido correcto. Se puede devolver la garantia de la reserva ', NEW."Deposit_returned");
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
   
    IF (NEW."Deposit_returned" IS NOT NULL) THEN
        NEW."Status" := 'finalizada';
    END IF;

  END IF;

  -- A FINALIZADA
  -- Se confirma que el usuario abandona el alojamiento en perfectas condiciones
  IF (NEW."Status" = 'finalizada') THEN
    -- Log
    change := CONCAT('Reserva finalizada ', CURRENT_DATE);  
  END IF;

  -- Registra el cambio
  IF change IS NOT NULL THEN
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
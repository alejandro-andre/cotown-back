-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;
  record_id INTEGER = 0;
  curr_user VARCHAR;

BEGIN

  -- Por defecto, deshabilita el botón de envío de alternativas
  IF (NEW."Status" <> 'solicitud' AND NEW."Status" <> 'solicitudpagada') THEN
    NEW."Button_options" := '';
  END IF;

  -- SOLICITUD a PENDIENTE DE PAGO
  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso a una solicitud no pagada
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" :='pendientepago';
  END IF;

  -- PENDIENTE DE PAGO A CADUCADA
  -- Actualiza al estado 'Pendiente de pago' cuando la solicitud ya no esta caducada
   IF (NEW."Status" = 'pendientepago' AND NEW."Expiry_date" < CURRENT_DATE)  THEN
    NEW."Status" :='caducada';
  END IF;

  -- CADUCADA A PENDIENTE DE PAGO
  -- Actualiza al estado 'Pendiente de pago' cuando la solicitud esta caducada
   IF (NEW."Status" = 'caducada' AND NEW."Expiry_date" >= CURRENT_DATE)  THEN
    NEW."Status" :='pendientepago';
  END IF;

  -- SOLICITUD PAGADA o ALTERNATIVA PAGADA a CONFIRMADA
  -- Actualiza al estado 'Confirmada' cuando se asigna el recurso a una solicitud pagada
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN
    -- Si hay que pagar garantía, pasa a confirmada
    IF NEW."Deposit" > 0 THEN
      NEW."Status" := 'confirmada';
    -- Si no hay que pagar garantía, pasa a firma contrato
    ELSE
      NEW."Deposit_actual" = 0;
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
  IF (NEW."Status" = 'contrato' AND NEW."Contract_signed" IS NULL) THEN
    NEW."Status" := 'firmacontrato';
  END IF;
  
  -- CONTRATO a CHECK IN CONFIRMADO
  -- Actualiza al estado 'Checkin confirmado' cuando se asigna la fecha de checkin
  IF (NEW."Status" = 'contrato' AND NEW."Check_in" IS NOT NULL) THEN
    NEW."Status" := 'checkinconfirmado';
  END IF;

  -- FIRMA CONTRATO a CANCELADA 
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'firmacontrato'
  IF (NEW."Status" = 'firmacontrato' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CONTRATO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'contrato'
  IF (NEW."Status" = 'contrato' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECK IN CONFIRMADO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in confirmado'
  IF (NEW."Status" = 'checkinconfirmado' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECKIN a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'checkin' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- DESCARTADA PAGADA a DESCARTADA
  -- Actualiza el estado a "descartada" cuando se devuelve el booking fee
  IF (NEW."Status" = 'descartadapagada' AND NEW."Booking_fee_returned" IS NOT NULL) THEN
    NEW."Status" := 'descartada';
  END IF;

  -- DEVOLVER GARANTIA a FINALIZADA
  -- Actualiza el estado a "finalizada" cuando se devuelve la garantía
  IF (NEW."Status" = 'devolvergarantia' AND NEW."Deposit_returned" IS NOT NULL) THEN
    NEW."Status" := 'finalizada';
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
 
  -- A ALTERNATIVA o ALTERNATIVAS PAGADA
  IF (NEW."Status" = 'alternativas' OR NEW."Status" = 'alternativaspagada') THEN
    -- Email
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'alternativas', NEW.id);
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
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'pendientepago', NEW.id);
    -- Log
    change := 'Pendiente de pago';
  END IF;

  -- A CADUCADA
	IF (NEW."Status" = 'caducada') THEN
		-- Envia email informando de la caducidad
		INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'caducada', NEW.id);
		-- Log
		change := CONCAT('La solicitud ha caducado el día ', NEW."Expiry_date");
	END IF;

  -- A CONFIRMADA 
  -- Inserta pago de garantía pendiente y envía mail
  IF (NEW."Status" = 'confirmada') THEN
    -- Borra fecha expiración
    NEW."Expiry_date" := NULL;
    -- Actualiza la fecha de confirmación
    NEW."Confirmation_date" := CURRENT_DATE;
    -- Borramos las alternativas asociadas a la solicitud
    DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."id";
    -- Depósito
    DELETE FROM "Billing"."Payment" WHERE "Booking_id" =  NEW."id" AND "Payment_date" IS NULL and "Payment_type" = 'deposito' ;
    IF (NEW."Deposit" > 0 ) THEN
      INSERT INTO "Billing"."Payment" ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )  VALUES (COALESCE(NEW."Payment_method_id", 1), NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');
    END IF;
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);
    -- Log
    change := 'Reserva confirmada';
  END IF;

  -- A DESCARTADA PAGADA
  IF (NEW."Status" = 'descartadapagada') THEN
    -- Quita el recurso
    NEW."Resource_id" := NULL;
    -- EMail 
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartadapagada', NEW.id);
    -- Log
    change := 'Solicitud descartada y booking pagado.';   
  END IF;

  -- A DESCARTADA
  IF (NEW."Status" = 'descartada') THEN
    -- Quita el recurso
    NEW."Resource_id" := NULL;
    -- Eliminamos el registro de pago del booking, si existe, ya que no ha sido pagado.
    DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id;
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartada', NEW.id);
    -- Log
    change := CONCAT('Solicitud descartada. ');
    IF(NEW."Booking_fee_returned" IS NOT NULL) THEN
      change := CONCAT(change, 'Hay que devolver el booking con por importe de: ', NEW."Booking_fee_returned"); 
    END IF; 
  END IF;

  -- A FIRMA CONTRATO
  IF (NEW."Status" = 'firmacontrato') THEN 
    -- EMail 
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'firmacontrato', NEW.id);
    -- Log 
    change := 'Pendiente de firmar el contrato de la reserva'; 
  END IF;

  -- A CONTRATO
  IF (NEW."Status" = 'contrato') THEN 
      -- Log 
      change := CONCAT('Firmado contrato de la reserva ', NEW."Contract_signed"); 
  END IF;

  -- A CHECK IN CONFIRMADO
  IF (NEW."Status" = 'checkinconfirmado' OR (NEW."Status" = 'checkin' AND OLD."Status" = 'contrato')) THEN 
    -- Email
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'checkinconfirmado', NEW.id);
    -- Log 
    change := CONCAT('Confirmada la fecha de checkin de la reserva ', NEW."Check_in"); 
  END IF;

  -- A CANCELADA (BOTON CANCELAR EN EL AREA PRIVADA)
  -- Cancelada, elimina pago pendiente de garantia y envía mail
  IF (NEW."Status" = 'cancelada') THEN     

    -- Eliminamos facturas no pagadas ??
    DELETE  FROM "Billing"."Invoice"
    WHERE "Payment_id" IN (
      SELECT "Invoice"."Payment_id" FROM "Billing"."Payment", "Billing"."Invoice" 
      WHERE "Payment"."Booking_id" = NEW.id 
      AND "Payment"."Payment_date" IS null
      AND "Payment"."id" = "Invoice"."Payment_id");

    -- Eliminamos cualquier registro de pago no ha pagado.
    DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id AND "Payment_date" IS NULL;
    -- Actualizamos la fecha de cancelación
    NEW."Cancel_date" := CURRENT_DATE;
    -- Eliminamos el recurso asignado
    NEW."Resource_id" = NULL;
    -- TODO: Calcular penalizacion
    IF(NEW."Cancelation_fee" > 0) THEN
      -- EMail con penalizacion
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'canceladapenalizacion', NEW.id);
      -- Log
      change := CONCAT('Reserva cancelada con penalización. Penalización: ', NEW."Cancelation_fee"); 
    ELSE
      -- EMail sin penalizacion
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'cancelada', NEW.id);
      -- Log
      change := 'Reserva cancelada sin penalización';   
    END IF; 
    
       
  END IF;

  -- A IN HOUSE (BOTON 'CHECK IN OK')
  -- Se confirma la llegada del usuario al alojamiento
  IF (NEW."Status" = 'inhouse') THEN  
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'inhouse', NEW.id);
    -- Log
    change := 'Se confirma que el usuario ha llegado al alojamiento.';   
  END IF;

  -- A DEVOLVER GARANTIA (BOTON 'CHECK OUT OK')
  -- Se confirma que el usuario abandona el alojamiento en perfectas condiciones
  IF (NEW."Status" = 'devolvergarantia') THEN 
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'devolvergarantia', NEW.id);
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
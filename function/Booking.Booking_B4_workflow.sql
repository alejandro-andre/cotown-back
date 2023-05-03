-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;
  record_id INTEGER = 0;

BEGIN

  RESET ROLE;
  
  -- SOLICITUD a PENDIENTEDEPAGO
  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso a una solicitud no pagada
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" :='pendientepago';
  END IF;

  -- PENDIENTE DE PAGO A CADUCADA
  -- Actualiza al estado 'Pendiente de pago' cuando la solicitud esta caducada
   IF (NEW."Status" = 'caducada' AND NEW."Expiry_date" >= CURRENT_DATE)  THEN
    NEW."Status" :='pendientepago';
  END IF;

  -- SOLICITUDPAGADA, ALTERNATIVAPAGADA a CONFIRMADA
  -- Actualiza al estado 'Confirmada' cuando se asigna el recurso a una solicitud pagada
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" := 'confirmada';
  END IF;

  -- FIRMACONTRATO a CONTRATO
  -- Actualiza el estado a "contrato" desde 'firmacontrato' cuando firma el contrado (Fecha contract_signed rellena)
  IF (NEW."Status" = 'firmacontrato' AND NEW."Contract_signed" IS NOT NULL) THEN
    NEW."Status" := 'contrato';
  END IF;

  -- CONTRATO a FIRMACONTRATO
  -- Actualiza el estado a "firmacontrato" cuando se quita la firma, tiene que firmarse el contrato nuevamente
  IF (NEW."Status" = 'contrato' AND NEW."Contract_signed" IS NULL) THEN
    NEW."Status" := 'firmacontrato';
  END IF;
  
  -- CONTRATO a CHECKINCONFIRMADO
  -- Actualiza al estado 'Checkin confirmado' cuando se asigna la fecha de checkin
  IF (NEW."Status" = 'contrato' AND NEW."Check_in" IS NOT NULL) THEN
    NEW."Status" := 'checkinconfirmado';
  END IF;

  -- FIRMACONTRATO a CANCELADA 
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'firmacontrato'
  IF (NEW."Status" = 'firmacontrato' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CONTRATO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'contrato'
  IF (NEW."Status" = 'contrato' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECKINCONFIRMADO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in confirmado'
  IF (NEW."Status" = 'checkinconfirmado' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECKIN a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'checkin' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- No ha habido cambios de estado
  IF (NEW."Status" = OLD."Status") THEN
    RETURN NEW;
  END IF;




  -- ALTERNATIVA o ALTERNATIVASPAGADA
  IF (NEW."Status" = 'alternativas' OR NEW."Status" = 'alternativaspagada') THEN
    -- Email
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'alternativas', NEW.id);
    -- Log
    change := 'Revisar alternativas';
  END IF;

  -- A PENDIENTEDEPAGO
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

  -- CONFIRMADA 
  -- Inserta pago de garantía pendiente y envía mail
  IF (NEW."Status" = 'confirmada' ) THEN
    -- Borra fecha expiración
    NEW."Expiry_date" := NULL;
    -- Actualiza la fecha de confirmación
    NEW."Confirmation_date" := CURRENT_DATE;
    -- Borramos las alternativas asociadas a la solicitud
    DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."id";
    -- Depósito
    IF (NEW."Deposit" > 0) THEN
      INSERT INTO "Billing"."Payment" ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )  VALUES (COALESCE(NEW."Payment_method_id", 1), NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');
    END IF;
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);
    -- Log
    change := 'Reserva confirmada';
  END IF;

  -- A DESCARTADAPAGADA
  IF (NEW."Status" = 'descartadapagada') THEN
    --?? GENERAR REGISTRO DE DEVOLUCION

    -- EMail 
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartadapagada', NEW.id);
    -- Log
    change := 'Solicitud descartada. Hay que devolver el pago del booking';   
  END IF;

  -- A DESCARTADA
  IF (NEW."Status" = 'descartada') THEN
      -- Eliminamos el registro de pago del booking, si existe, ya que no ha sido pagado.
      DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id;
      -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartada', NEW.id);
      -- Log
      change := 'Solicitud descartada.';   
  END IF;

  -- A FIRMACONTRATO
  IF (NEW."Status" = 'firmacontrato') THEN 
    -- EMail 
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'firmacontrato', NEW.id);
    -- Log 
    change := CONCAT('Pendiente de firmar el contrato de la reserva ', NEW.id) ; 
  END IF;

  -- A CONTRATO
  IF (NEW."Status" = 'contrato') THEN 
      -- Log 
      change := CONCAT('Firmado contrato de la reserva ', NEW."Contract_signed") ; 
  END IF;

  -- A CHECKINCONFIRMADO
  IF (NEW."Status" = 'checkinconfirmado') THEN 
    -- Email
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'checkinconfirmado', NEW.id);
    -- Log 
    change := CONCAT('Confirmada la fecha de checkin de la reserva ', NEW."Check_in") ; 
  END IF;

  -- CONFIRMADA a CANCELADA (BOTON CANCELAR EN EL AREA PRIVADA)
  -- Cancelada, elimina pago pendiente de garantia y envía mail
  IF (NEW."Status" = 'cancelada') THEN              
    -- Eliminamos cualquier registro de pago no ha pagado.
    DELETE FROM "Billing"."Payment" WHERE "Booking_id" = NEW.id AND "Payment_date" IS NULL;
    -- Actualizamos la fecha de cancelación
    NEW."Cancel_date" := CURRENT_DATE;
    -- TODO: Calcular penalizacion
    
    -- EMail 
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'cancelada', NEW.id);
    -- Log
    change := 'Reserva cancelada antes de pagar la garantia';   
  END IF;

  -- AINHOUSE (BOTON 'CHECK IN OK')
  -- Se confirma la llegada del usuario al alojamiento
  IF (NEW."Status" = 'inhouse') THEN  
    -- EMail
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'inhouse', NEW.id);
    -- Log
    change := 'Se confirma que el usuario ha llegado al alojamiento.';   
  END IF;

  -- A DEVOLVERGARANTIA (BOTON 'CHECKOUT OK')
  -- Se confirma que el usuario abandona el alojamiento en perfectas condiciones
  IF (NEW."Status" = 'devolvergarantia') THEN 
    --?? GENERAR REGISTRO DE DEVOLUCION

    -- Log
    change := CONCAT('El checkout ha sido correcto. Se puede devolver la garantia de la reserva ', NEW.id);   
  END IF;

  -- Registra el cambio
  IF change IS NOT NULL THEN
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
  END IF;

  RETURN NEW;

END;
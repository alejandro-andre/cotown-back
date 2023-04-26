-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;
  record_id INTEGER;

BEGIN

  RESET ROLE;
  
  -- SOLICITUD a PENDIENTEDEPAGO. 
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

  -- CONTRATO a CHECKINCONFIRMADO
  -- Actualiza al estado 'Checkin confirmado' cuando se asigna la fecha de checkin
  IF (NEW."Status" = 'contrato' AND NEW."Check_in" IS NOT NULL) THEN
    NEW."Status" := 'checkinconfirmado';
  END IF;

 -- SOLICITUDPAGADA a DESCARTADAPAGADA
 -- Actualiza el estado a "descartadapagada" cuando se cancela una reserva en estado 'solicitudpagada'
 -- IF (NEW."Status" = 'solicitudpagada' AND NEW."Cancel_date" IS NOT NULL AND NEW."Resource_id" IS NULL) THEN
 --   NEW."Status" := 'descartadapagada';
 -- END IF; 
  
  -- CONFIRMADA a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'confirmada'
  -- IF (NEW."Status" = 'confirmada' AND NEW."Cancel_date" IS NOT NULL AND  NEW."Resource_id" IS NULL) THEN
  --  NEW."Status" := 'cancelada';
  -- END IF;

  -- CONFIRMADA a SOLICITUDPAGADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'confirmada'
  IF (NEW."Status" = 'confirmada' AND  NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'solicitudpagada';
  END IF;

  

  -- CONTRATO a FIRMACONTRATO 
  -- Actualiza el estado a "ckeckinconfirmado" desde 'firmacontrato' cuando firma el contrado e introduce la fecha de checkin 
  IF (NEW."Status" = 'firmacontrato' AND (NEW."Contract_signed" IS NOT NULL AND NEW."Check_in" IS NOT NULL)) THEN
       NEW."Status" := 'checkinconfirmado';
  END IF;
  -- Actualiza el estado a "contrato" desde 'firmacontrato' cuando firma el contrado (Fecha contract_signed rellena)
  IF (NEW."Status" = 'firmacontrato' AND (NEW."Contract_signed" IS NOT NULL AND NEW."Check_in" IS  NULL)) THEN
       NEW."Status" := 'contrato';
  END IF;


  -- FIRMACONTRATO a CONTRATO
  -- Actualiza el estado a "firmacontrato" cuando se pasa a estado 'contrato'. Tiene que firmarse el contrato nuevamente
  IF (NEW."Status" = 'contrato' AND NEW."Contract_signed" IS NULL) THEN
    NEW."Status" := 'firmacontrato';
  END IF;
  

-- FIRMACONTRATO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'firmacontrato'
  IF (NEW."Status" = 'firmacontrato' AND NEW."Cancel_date" IS NOT NULL AND NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CONTRATO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'contrato'
  IF (NEW."Status" = 'contrato' AND NEW."Cancel_date" IS NOT NULL AND NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECKINCONFIRMADO a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'checkinconfirmado' AND NEW."Cancel_date" IS NOT NULL ) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- CHECKIN a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'checkin' AND NEW."Cancel_date" IS NOT NULL ) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- INHOUSE a CANCELADA
  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'inhouse' AND NEW."Cancel_date" IS NOT NULL AND NEW."Cancelation_fee" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;
 

  -- Cambios de estado
  IF (NEW."Status" <> OLD."Status") THEN

    -- SOLICITUD, SOLICITUDPAGADA a ALTERNATIVA, ALTERNATIVASPAGADA
    IF ((OLD."Status" = 'solicitud' AND NEW."Status" = 'alternativas') OR
       (OLD."Status" = 'solicitudpagada' AND NEW."Status" = 'alternativaspagada')) THEN

      -- Email
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'alternativas', NEW.id);

      -- Log
      change := 'Revisar alternativas';

    END IF;

    -- SOLICITUD a PENDIENTEDEPAGO.
    -- Pendiente de pago, envía mail
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

    -- CONFIRMADA a FIRMACONTRATO
     IF (NEW."Status" = 'firmacontrato' AND OLD."Status" = 'confirmada') THEN 
      -- Actualizamos la fecha de la firma del contrato
         UPDATE "Booking"."Booking" SET "Contract_signed" = CURRENT_DATE WHERE "Booking".id = NEW.id;
      -- Borramos las alternativas asociadas a la solicitud
         DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."Booking_id";
      -- EMail 
         INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'firmacontrato', NEW.id);
        -- Log 
        change := CONCAT('Pendiente de firmar el contrato de la reserva ', NEW.id) ; 
     END IF;

    -- CONTRATO a CHECKINCONFIRMADO
    -- Confirmación de la fecha de checkin 
     IF (NEW."Status" = 'checkinconfirmado') THEN 
        -- Log 
        change := CONCAT('Confirmada la fecha de checkin de la reserva ', NEW."Check_in") ; 
        -- Email
        INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'checkinconfirmado', NEW.id);
     END IF;

     -- SOLICITUDPAGADA a DESCARTADAPAGADA
    IF (NEW."Status" = 'descartadapagada') THEN
        -- GENERAR REGISTRO DE DEVOLUCION ¿?
        -- Actualiza la fecha de cancelación
        UPDATE "Booking"."Booking" SET "Cancel_date" = CURRENT_DATE WHERE "Booking".id = NEW.id;
        -- EMail 
        INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartadapagada', NEW.id);
        -- Log
        change := 'Solicitud descartada. Hay que devolver el pago del booking';   
    END IF;

 -- SOLICITUD, ALTERNATIVAS, PENDIENTEPAGO a DESCARTADA
    IF (NEW."Status" = 'descartada') THEN
        -- Comprobamos si el booking esta pagado
        SELECT "id" INTO record_id 
        FROM "Billing"."Payment" 
        WHERE "Booking_id" = NEW."id" 
        AND "Payment_type" = 'booking'
        AND "Payment_auth" IS NOT NULL 
        AND "Payment_date" IS NOT NULL;
        IF(record_id = 1) THEN
            -- Eliminamos el registro de pago del deposito ya que no ha sido pagado.
            DELETE FROM "Billing"."Payment" WHERE id=record_id;
        END IF;
        -- Eliminamos el recurso asignado
        UPDATE "Booking"."Booking" SET "Resource_id" = NULL WHERE "Booking".id = NEW.id;
        -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
        INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'descartada', NEW.id);
        -- Log
        change := 'Solicitud descartada.';   
    END IF;


    -- CONFIRMADA a CANCELADA (BOTON CANCELAR EN EL AREA PRIVADA)
    -- Cancelada, elimina pago pendiente de garantia y envía mail
    IF (NEW."Status" = 'cancelada' AND OLD."Status" = 'confirmada') THEN              
              -- Comprobamos si la garantia/deposito esta pagada
              SELECT "id" INTO record_id 
              FROM "Billing"."Payment" 
              WHERE "Booking_id" = NEW."id" 
              AND "Payment_type" = 'deposito'
              AND "Payment_auth" IS NOT NULL 
              AND "Payment_date" IS NOT NULL;
              IF(record_id = 1) THEN
                    -- Eliminamos el registro de pago del deposito ya que no ha sido pagado.
                    DELETE FROM "Billing"."Payment" WHERE id=record_id;
              END IF;
              -- Actualizamos la fecha de cancelación
              UPDATE "Booking"."Booking" SET "Cancel_date" = CURRENT_DATE, "Resource_id" = NULL WHERE "Booking".id = NEW.id;
              -- EMail 
              INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);
              -- Log
              change := 'Reserva cancelada antes de pagar la garantia';   
 
    END IF;

    -- CONFIRMADA a SOLICITUDPAGADA
    IF (NEW."Status" = 'solicitudpagada' AND OLD."Status" = 'confirmada') THEN 
      -- Log
      change := CONCAT('Se ha desasignado el recurso de la solicitud ', NEW.id);   
    END IF;

    
    -- FIRMACONTRATO a CONTRATO
    IF (NEW."Status" = 'contrato' AND OLD."Status" = 'firmacontrato') THEN 
       -- Log 
        change := CONCAT('Firmado contrato de la reserva ', NEW."Contract_signed") ; 
    END IF;

     -- CONTRATO a FIRMACONTRATO
     -- Nueva disponsicion para firmar el contrato 
     IF (NEW."Status" = 'firmacontrato' AND OLD."Status" = 'contrato') THEN 
        -- Log 
        change := 'Nuevo contrato pendiente para ser firmado firmado '; 
     END IF;


    -- Confirmada, inserta pago de garantía pendiente y envía mail
    IF (NEW."Status" = 'confirmada' ) THEN

      -- Borra fecha expiración
      NEW."Expiry_date" = NULL;

      -- Depósito
      INSERT INTO "Billing"."Payment" ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )  VALUES (COALESCE(NEW."Payment_method_id", 1), NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');

      -- EMail
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

      -- Log
      change := 'Reserva confirmada';

      -- Borramos las alternativas asociadas a la solicitud
      DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."id";

    END IF;

   
    
    -- FIRMACONTRATO, CONTRATO, CHECKINCONFIRMADO, CHECKIN a CANCELADA
    -- Cancelada antes de firmar el contrato, despues de firmar el contrato, despues de confirmar el checkin, una vez realizado el checkin
    IF (NEW."Status" = 'cancelada'
      AND (OLD."Status" = 'firmacontrato'
      OR OLD."Status" = 'contrato' 
      OR OLD."Status" = 'checkinconfirmado' 
      OR OLD."Status" = 'checkin')) THEN              
              -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
              INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'cancelada', NEW.id);
              -- Log
              change := 'Reserva cancelada despues de pagar el depósito, despues de firmar el contrato';   
    END IF;

    -- INHOUSE a CANCELADA
    -- Cancelada una vez habitando el recurso. Crea pago de penalización y envía mail
    IF (NEW."Status" = 'cancelada' AND OLD."Status" = 'inhouse') THEN  
        -- crea un registro de pago de la penalización. 
        INSERT INTO "Billing"."Payment"("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES (COALESCE(NEW."Payment_method_id", 1), NEW."Customer_id", NEW.id, NEW."Cancelation_fee", CURRENT_DATE, 'Booking cancel', 'penalizacion');
         -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
        INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'canceladapenalizacion', NEW.id);
         -- Log
         change := 'Reserva cancelada con penalización';   
    END IF;

    -- CHECKIN a INHOUSE
    -- Se confirma la llegada del usuario al alojamiento
    IF (NEW."Status" = 'inhouse') THEN  
      -- EMail
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'inhouse', NEW.id);
      -- Log
      change := 'Se confirma que el usuario ha llegado al alojamiento.';   
    END IF;

    -- CHECKOUT a DEVOLVERGARANTIA
    -- Se confirma que el usuario abandona el alojamiento en perfectas condiciones
    IF (NEW."Status" = 'devolvergarantia') THEN 
      -- GENERAR REGISTRO DE DEVOLUCION (¿COMO SE HACE?)  
      -- EMail ¿Enviar email?
      -- Log
      change := CONCAT('El checkout ha sido correcto. Se puede devolver la garantia de la reserva ', NEW.id);   
    END IF;




  END IF;

  -- Registra el cambio
  IF change IS NOT NULL THEN
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
  END IF;

  RETURN NEW;

END;
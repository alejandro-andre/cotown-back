-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;
  record_id INTEGER;

BEGIN

  RESET ROLE;
  
  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso a una solicitud no pagada
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" :='pendientepago';
  END IF;
  
  -- Actualiza al estado 'Confirmada' cuando se asigna el recurso a una solicitud pagada
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" := 'confirmada';
  END IF;

  -- Actualiza al estado 'Checkin confirmado' cuando se asigna la fecha de checkin
  IF (NEW."Status" = 'contrato' AND NEW."Check_in" IS NOT NULL) THEN
    NEW."Status" := 'checkinconfirmado';
  END IF;


 -- Actualiza el estado a "devolvergarantia" cuando se cancela una reserva en estado 'solicitudpagada'
  IF (NEW."Status" = 'solicitudpagada' AND NEW."Cancel_date" IS NOT NULL  AND NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'devolvergarantia';
  END IF; 

  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'confirmada'
  IF (NEW."Status" = 'confirmada' AND NEW."Cancel_date" IS NOT NULL AND  NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'firmacontrato'
  IF (NEW."Status" = 'firmacontrato' AND NEW."Cancel_date" IS NOT NULL AND NEW."Cancelation_fee" IS NOT NULL AND NEW."Resource_id" IS NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;

  -- Actualiza el estado a "cancelada" cuando se cancela una reserva en estado 'check in'
  IF (NEW."Status" = 'checkin' AND NEW."Cancel_date" IS NOT NULL) THEN
    NEW."Status" := 'cancelada';
  END IF;
  

  -- Cambios de estado
  IF (NEW."Status" <> OLD."Status") THEN

    -- Alternativas, envía mail
    IF ((OLD."Status" = 'solicitud' AND NEW."Status" = 'alternativas') OR
       (OLD."Status" = 'solicitudpagada' AND NEW."Status" = 'alternativaspagada')) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'alternativa', NEW.id);
      change := 'Revisar alternativas';
    END IF;

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

    -- Confirmada, inserta pago de garantía pendiente y envía mail
    IF (NEW."Status" = 'confirmada' ) THEN

      -- Borra fecha expiración
      NEW."Expiry_date" = NULL;

      -- Depósito
      INSERT INTO "Billing"."Payment" ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )  VALUES ('1', NEW."Customer_id", NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');

      -- EMail
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

      -- Log
      change := 'Reserva confirmada';

      -- Borramos las alternativas asociadas a la solicitud
      DELETE FROM "Booking"."Booking_option" WHERE "Booking_id" = NEW."id";

    END IF;


    IF(NEW."Status" = 'devolvergarantia') THEN
        -- GENERAR REGISTRO DE DEVOLUCION ¿?

        -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
        --INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

        -- Log
        change := 'Solicitud cancelada. Hay que devolver la garantia';   
    END IF;

     -- Cancelada, elimina pago pendiente de garantia y envía mail
    IF (NEW."Status" = 'cancelada' AND OLD."Status" = 'confirmada') THEN              
              -- Comprobamos si la garantia esta pagada
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

              -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
              --INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

              -- Log
              change := 'Reserva cancelada antes de pagar la garantia';   
 
    END IF;

    -- Cancelada, antes de hacer chekcin. envía mail
    IF (NEW."Status" = 'cancelada' AND OLD."Status" = 'firmacontrato') THEN              
              -- crea un registro de pago de la penalización. ESTO ES CUANDO EL ESTADO ESTE EN CKECK IN
              -- INSERT INTO "Billing"."Payment"("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES ('1', NEW."Customer_id", NEW.id, NEW."Cancelation_fee", CURRENT_DATE, 'Booking cancel', 'penalizacion');

              -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
              --INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

              -- Log
              change := 'Reserva cancelada despues de pagar el depósito';   
 
    END IF;

    -- Cancelada, crea pago de penalización y envía mail
    IF (NEW."Status" = 'cancelada' AND OLD."Status" = 'checkin') THEN  
        -- crea un registro de pago de la penalización. 
        INSERT INTO "Billing"."Payment"("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES ('1', NEW."Customer_id", NEW.id, NEW."Cancelation_fee", CURRENT_DATE, 'Booking cancel', 'penalizacion');

              -- EMail (AÑADIR LA PLANTILLA CORRESPONDIENTE)
              --INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'confirmada', NEW.id);

              -- Log
              change := 'Reserva cancelada despues de hacer checkin';   
    END IF;

  END IF;

  -- Registra el cambio
  IF change IS NOT NULL THEN
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
  END IF;

  RETURN NEW;

END;
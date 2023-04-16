-- Workflow de reserva
DECLARE

  change VARCHAR = NULL;

BEGIN

  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso a una solicitud no pagada
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" :='pendientepago';
    NEW."Expiry_date" := (CURRENT_DATE + INTERVAL '2 days');
    change := 'Pendiente de pago';
  END IF;
  
  -- Actualiza al estado 'Confirmada' cuando se asigna el recurso a una solicitud pagada
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN
    NEW."Status" := 'confirmada';
    NEW."Expiry_date" = NULL;
    change := 'Reserva confirmada';
  END IF;

  -- Cambios de estado
  IF (NEW."Status" <> OLD."Status") THEN

    -- Confirmada, Pago de garantía pendiente
    IF (NEW."Status" = 'confirmada' ) THEN
      INSERT INTO "Billing"."Payment"("Payment_method_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) 
        VALUES ('1', NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');
    END IF;

  END IF;

  -- Registra el cambio
  IF change IS NOT NULL THEN
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
  END IF;

  RETURN NEW;

END;
-- bookingWorkflow
BEGIN

  -- Actualiza al estado 'Pendiente de pago' cuando se asigna el recurso
  IF ((NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas')AND NEW."Resource_id" IS NOT NULL) THEN

	-- Actualiza el estado
    NEW."Status" :='pendientepago';
    NEW."Expiry_date" := (CURRENT_DATE + INTERVAL '2 days');

	-- Registra el cambio
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Pendiente de pago');

  END IF;
  
  -- Actualizamos al estado 'Confirmada' cuando se asigna el recurso
  IF ((NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada') AND NEW."Resource_id" IS NOT NULL) THEN

	-- Actualiza el estado
    NEW."Status" := 'confirmada';
    NEW."Expiry_date" = NULL;

	-- Registra el cambio
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Reserva confirmada');

	-- Crea el pago de la garantía
    INSERT INTO "Billing"."Payment"("Payment_method_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES ('1', NEW.id, NEW."Deposit", CURRENT_DATE, 'Booking deposit', 'deposito');  

  END IF;
  
  RETURN NEW;

END;
-- paymentWorkflow
DECLARE

  status_record VARCHAR;

BEGIN

  -- Comprobamos si el pago se ha llevado a cabo correctamente 
  IF (NEW."Payment_auth" IS NULL OR NEW."Payment_date" IS NULL) THEN 
    RETURN NEW;
  END IF;

  -- Seleccionamos el estado actual de la reserva
  SELECT "Status" INTO status_record FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
  
  -- Comprobamos si el tipo de pago es 'booking'
  IF (NEW."Payment_type" = 'booking') THEN

    -- Registra el pago
    INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW."Booking_id", 'Booking fee pagado');

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

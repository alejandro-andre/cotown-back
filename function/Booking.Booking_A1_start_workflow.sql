-- Inicio del workflow de reserva
BEGIN

  -- Alta en estado diferente de solictud
  IF NEW."Status" IS NOT NULL AND NEW."Status" <> 'solicitud' THEN
    RETURN NEW;
  END IF;
  
  -- Estado solicitud
  UPDATE "Booking"."Booking" SET "Status" = 'solicitud' WHERE id = NEW.id;

  -- Obtiene crea un pago con el booking fee
  INSERT INTO "Billing"."Payment"("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES (COALESCE(NEW."Payment_method_id", 1), NEW."Customer_id", NEW.id, NEW."Booking_fee", CURRENT_DATE, 'Booking fee', 'booking');

  -- Log
  INSERT INTO "Booking"."Booking_log"("Booking_id", "Log") VALUES (NEW.id, 'Solicitud de recurso');

  -- Email
  INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'solicitud', NEW.id);

  RETURN NEW;

END;
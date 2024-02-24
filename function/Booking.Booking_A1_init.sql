-- Inicio del workflow de reserva
DECLARE

  curr_user VARCHAR;
  payment_method_id INTEGER = 1;

BEGIN

  -- Alta en estado diferente de solictud
  IF NEW."Status" IS NOT NULL AND NEW."Status" <> 'solicitud' THEN
    RETURN NEW;
  END IF;
 
  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Crea un pago con el booking fee
  IF NEW."Booking_fee" > 0 THEN
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";
    INSERT
      INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
      VALUES (COALESCE(payment_method_id, 1), 'cotown', NEW."Customer_id", NEW.id, NEW."Booking_fee", CURRENT_DATE, 'Booking fee', 'booking');
  END IF;
 
  -- Log
  INSERT INTO "Booking"."Booking_log"("Booking_id", "Log") VALUES (NEW.id, 'Solicitud de recurso');

  -- Create user if not existing yet (WARNING!)
  UPDATE "Customer"."Customer" SET "User_name" = NULL WHERE id = NEW."Customer_id" AND "User_name" LIKE 'N%';

  -- Email
  IF NEW."Origin_id" IS NULL THEN
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'solicitud', NEW.id);
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
DECLARE
  current_booking INTEGER;
BEGIN
  SELECT MAX(id) INTO current_booking FROM "Booking"."Booking";  
  UPDATE "Booking"."Booking" SET "Status" = 'solicitud' WHERE id = current_booking;
  INSERT INTO "Booking"."Booking_log"("Booking_id", "Log") VALUES (current_booking, 'Solicitud de recurso');
  INSERT INTO "Billing"."Payment"("Payment_method_id", "Booking_id", "Amount", "Issued_date", "Concept" ) VALUES ('1',current_booking, 100, CURRENT_DATE, 'Booking fee');
  RETURN NEW;
END;
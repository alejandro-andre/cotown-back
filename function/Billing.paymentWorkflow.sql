-- Pasa una solicitud a pagada cuando se paga el booking fee
DECLARE

  total_records INTEGER;

BEGIN

  SELECT count(*) 
  INTO total_records 
  FROM "Billing"."Payment"
  WHERE "Booking_id" = NEW."Booking_id"
  AND "Payment_order" IS NOT NULL
  AND "id" = NEW.id;
  
  IF (total_records = 1) THEN
    UPDATE "Booking"."Booking" SET "Status" ='solicitudpagada' WHERE id=NEW."Booking_id";
    UPDATE "Booking"."Booking_log" SET "Log" = 'Solicitud pagada' WHERE "Booking_id" = NEW."Booking_id";
  END IF;

  RETURN NEW;

END;
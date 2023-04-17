-- Cancelacion de la solicitud confirmada
  DECLARE

  change VARCHAR = NULL;
  deposit_paid INTEGER;

BEGIN

  RESET ROLE;
  
  IF booking_status = 'cancelada' and THEN
    SELECT COUNT(*) INTO deposit_paid FROM "Billing"."Payment" WHERE "Booking".id = NEW."Booking_id";
    IF(deposit_paid >0) THEN
        INSERT INTO "Billing"."Payment"("Payment_method_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES ('1',NEW."id", NEW."Cancelation_fee", CURRENT_DATE, 'Booking cancel', 'penalización');
        -- falta log
    END IF;
  END IF;

END;

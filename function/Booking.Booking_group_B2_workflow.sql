-- Workflow
DECLARE

  status "Auxiliar"."Group_status";
  payment_method_id INTEGER;

BEGIN

  -- Status
  status := NEW."Status";

  -- Tentative
  IF status = 'grupobloqueado' THEN
    IF NEW."Confirmation_date" IS NOT NULL THEN
      status = 'grupoconfirmado';

	  -- Membership fee
	  IF NEW."Booking_fee" > 0 THEN
	
	    -- Receipt exist
	    IF EXISTS (SELECT 1 FROM "Billing"."Payment" WHERE "Payment_type" = 'booking' AND "Customer_id" = NEW."Payer_id" AND "Booking_group_id" = NEW.id) THEN
	      RAISE EXCEPTION '!!!Membership fee payment already issued!!!El pago del Membership fee ya fue emitido!!!';
	    END IF;
	
	    -- Add payment
	    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Payer_id";
	    INSERT
	      INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
	      VALUES (COALESCE(payment_method_id, 2), NULL, NEW."Payer_id", NEW.id, NEW."Rooms" * NEW."Booking_fee", CURRENT_DATE, 'Membership fee', 'booking');
	    
	  END IF;
	
    END IF;
  END IF;

  -- Confirmed
  IF status = 'grupoconfirmado' THEN
    IF NEW."Confirmation_date" IS NULL THEN
      status = 'grupobloqueado';
    ELSE
      IF NEW."Date_from" <= CURRENT_DATE THEN
	      status = 'inhouse';
      END IF;	
    END IF;
  END IF;

  -- In house
  IF status = 'inhouse' THEN
    IF NEW."Date_to" <= CURRENT_DATE THEN
       status = 'revision';
    END IF;	
  END IF;

  -- Revision
  IF status = 'revision' THEN
    IF NEW."Deposit_required" IS NOT NULL AND NEW."Date_deposit_required" IS NOT NULL THEN  
      status = 'devolvergarantia';
    END IF;	
  END IF;

  -- Return deposit
  IF status = 'devolvergarantia' THEN
    IF NEW."Deposit_returned" IS NOT NULL AND NEW."Date_deposit_returned" IS NOT NULL THEN  
      status = 'finalizada';
    END IF;	
  END IF;

  -- Deposit
  IF NEW."Deposit_actual" > 0 AND COALESCE(OLD."Deposit_actual", 0) <> COALESCE(NEW."Deposit_actual", 0) THEN

    -- Receipt exist
    IF EXISTS (SELECT 1 FROM "Billing"."Payment" WHERE "Payment_type" = 'deposito' AND "Customer_id" = NEW."Payer_id" AND "Booking_group_id" = NEW.id) THEN
      RAISE EXCEPTION '!!!Deposit payment already issued!!!El pago de la garantía ya fue emitido!!!';
    END IF;

    -- Add payment
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Payer_id";
    INSERT
      INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
      VALUES (COALESCE(payment_method_id, 2), NULL, NEW."Payer_id", NEW.id, NEW."Deposit_actual", CURRENT_DATE, 'Garantía', 'deposito');
    
  END IF;

  -- Update status
  IF status <> NEW."Status" OR (status IS NOT NULL AND NEW."Status" IS NULL) THEN
    NEW."Status" = status;
  END IF;

  -- Return record
  RETURN NEW;

END;
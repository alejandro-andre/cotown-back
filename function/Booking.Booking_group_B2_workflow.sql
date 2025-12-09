-- Workflow
DECLARE

  status "Auxiliar"."Group_status";
  curr_user VARCHAR;
  payment_method_id INTEGER;
  payment_id INTEGER;
  invoice_id INTEGER;
  owner_id INTEGER;
  flat_id INTEGER;
  room_id INTEGER;

BEGIN

  -- Status
  status := NEW."Status";

    -- Superuser
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Tentative
  IF status IS NULL OR status = 'grupobloqueado' THEN
    IF NEW."Confirmation_date" IS NOT NULL THEN
      status = 'grupoconfirmado';

      -- Membership fee
      IF NEW."Booking_fee" > 0 THEN 
  
        -- Receipt exist
        IF EXISTS (SELECT 1 FROM "Billing"."Payment" WHERE "Payment_type" = 'booking' AND "Customer_id" = NEW."Payer_id" AND "Booking_group_id" = NEW.id) THEN
          RAISE EXCEPTION '!!!Membership fee payment already issued!!!El pago del Membership fee ya fue emitido!!!';
        END IF;
  
        -- Add payment
        SELECT "Resource_id" into room_id FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id LIMIT 1;
        IF room_id IS NULL THEN
          RAISE EXCEPTION '!!!No places assigned!!!Ni hay plazas asignadas!!!';
        END IF;
        SELECT COALESCE("Flat_id", id), "Owner_id" INTO flat_id, owner_id FROM "Resource"."Resource" r WHERE r.id = room_id;
        SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Payer_id";
        INSERT
          INTO "Billing"."Payment"("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (COALESCE(payment_method_id, 2), NULL, NEW."Payer_id", NEW.id, NEW."Rooms" * NEW."Booking_fee", CURRENT_DATE, 'Membership fee', 'booking')
        RETURNING id INTO payment_id;
        INSERT 
          INTO "Billing"."Invoice" ("Bill_type", "Issued", "Rectified", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
          VALUES ('factura', FALSE, FALSE, 1, NEW."Payer_id", NEW.id, COALESCE(payment_method_id, 2), payment_id, 'Membership fee')
          RETURNING id INTO invoice_id;
        INSERT
          INTO "Billing"."Invoice_line" ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept", "Resource_id")
          VALUES (invoice_id, NEW."Rooms" * NEW."Booking_fee", 1, 1, 'Membership fee', flat_id);
        UPDATE "Billing"."Invoice" SET "Issued" = TRUE WHERE id = invoice_id;

      END IF;

      -- Deposit
      IF NEW."Deposit" > 0 AND COALESCE(NEW."Deposit_actual", 0) = 0 THEN
        NEW."Deposit_actual" = NEW."Deposit" * NEW."Rooms";
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

    -- Add payment and invoice
    SELECT "Resource_id" into room_id FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id LIMIT 1;
    IF room_id IS NULL THEN
      RAISE EXCEPTION '!!!No places assigned!!!Ni hay plazas asignadas!!!';
    END IF;
    SELECT COALESCE("Flat_id", id), "Owner_id" INTO flat_id, owner_id FROM "Resource"."Resource" r WHERE r.id = room_id;
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Payer_id";
    INSERT
      INTO "Billing"."Payment" ("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
      VALUES (COALESCE(payment_method_id, 2), NULL, NEW."Payer_id", NEW.id, NEW."Deposit_actual", CURRENT_DATE, 'Garantía', 'deposito')
    RETURNING id INTO payment_id;
    INSERT 
      INTO "Billing"."Invoice" ("Bill_type", "Issued", "Rectified", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
      VALUES ('recibo', FALSE, FALSE, owner_id, NEW."Payer_id", NEW.id, COALESCE(payment_method_id, 2), payment_id, 'Garantía')
      RETURNING id INTO invoice_id;
    INSERT
      INTO "Billing"."Invoice_line" ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept", "Resource_id")
      VALUES (invoice_id, NEW."Deposit_actual", 2, 2, 'Garantía', flat_id);
    UPDATE "Billing"."Invoice" SET "Issued" = TRUE WHERE id = invoice_id;

  END IF;

  -- Update status
  IF status <> NEW."Status" OR (status IS NOT NULL AND NEW."Status" IS NULL) THEN
    NEW."Status" = status;
  END IF;

  -- Return record
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
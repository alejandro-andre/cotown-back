-- Copia la factura de otra
-- BEFORE INSERT
DECLARE

  invoice_id INTEGER;

  bill_type VARCHAR;
  provider_id INTEGER;
  customer_id INTEGER;
  booking_id INTEGER;
  booking_group_id INTEGER; 
  concept VARCHAR; 
  comments VARCHAR;
  payment_method_id INTEGER;

BEGIN

  -- New invoice
  IF NEW."Duplicate_id" IS NULL THEN
    RETURN NEW;
  END IF;

  -- Get invoice
  SELECT i."Bill_type", i."Provider_id", i."Customer_id", i."Booking_id", i."Booking_group_id", i."Concept", i."Comments", i."Payment_method_id"
  INTO bill_type, provider_id, customer_id, booking_id, booking_group_id, concept, comments, payment_method_id
  FROM "Billing"."Invoice" i 
  WHERE i.id = NEW."Duplicate_id";

  -- Not found
  IF NOT FOUND THEN
    RAISE EXCEPTION '!!!Invoice not found!!!Factura no encontrada!!!';
  END IF;

  -- Duplicate invoice
  NEW."Bill_type"         := COALESCE(NEW."Bill_type", bill_type::"Auxiliar"."Bill_type");
  NEW."Provider_id"       := COALESCE(NEW."Provider_id", provider_id);
  NEW."Customer_id"       := COALESCE(NEW."Customer_id", customer_id);
  NEW."Booking_id"        := COALESCE(NEW."Booking_id", booking_id);
  NEW."Booking_group_id"  := COALESCE(NEW."Booking_group_id", booking_group_id);
  NEW."Concept"           := COALESCE(NEW."Concept", concept);
  NEW."Comments"          := COALESCE(NEW."Comments", comments);
  NEW."Payment_method_id" := COALESCE(NEW."Payment_method_id", payment_method_id);

  -- Return
  RETURN NEW;

END;
-- Servicios adicionales
DECLARE

  tax_id INTEGER;
  concept VARCHAR;
  customer_id INTEGER;
  payment_method_id INTEGER;

  date_from DATE;
  date_to DATE;

BEGIN
	
  -- Validate dates
  SELECT "Date_from", "Date_to", "Customer_id" INTO date_from, date_to, customer_id FROM "Booking"."Booking" WHERE id = NEW."Booking_id";
  IF NEW."Billing_date_from" < date_from THEN
    RAISE exception '!!!Billing date cannot be earlier than the start of the reservation!!!Fecha de factura no puede ser anterior al inicio de la reserva!!!';
  END IF;
  IF NEW."Billing_date_to" IS NOT NULL THEN
    IF NEW."Billing_date_to" <= NEW."Billing_date_from" THEN
      RAISE exception '!!!Billing end date cannot be earlier than the start of the billing!!!Facturación hasta no puede ser anterior al inicio de la facturación!!!';
    END IF;
  END IF; 

  -- Provider: Cotown
  NEW."Provider_id" := 1;

  -- Tax
  IF NEW."Tax_id" IS NULL THEN
    SELECT "Tax_id" INTO tax_id FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Tax_id" := tax_id;
  END IF;

  -- Concept
  IF NEW."Concept" IS NULL THEN
    SELECT "Name" INTO concept FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Concept" := concept;
  END IF;

  -- Payment method
  IF NEW."Payment_method_id" IS NULL THEN
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = customer_id;
    NEW."Payment_method_id" := payment_method_id;
  END IF;

  -- Return record 
  RETURN NEW;

END;
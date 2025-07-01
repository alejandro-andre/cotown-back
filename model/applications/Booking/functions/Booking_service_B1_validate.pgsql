-- Servicios adicionales
DECLARE

  tax_id INTEGER;
  product_type INTEGER;
  concept VARCHAR;
  customer_id INTEGER;
  owner_id INTEGER;
  resource_id INTEGER;
  payment_method_id INTEGER;

  date_from DATE;
  date_to DATE;

BEGIN
	
  -- Booking data
  SELECT "Date_from", "Date_to", "Customer_id", "Resource_id" INTO date_from, date_to, customer_id, resource_id FROM "Booking"."Booking" WHERE id = NEW."Booking_id";

  -- Validate dates
  IF NEW."Billing_date_from" < date_from THEN
  --  RAISE exception '!!!Billing date cannot be earlier than the start of the reservation!!!Fecha de factura no puede ser anterior al inicio de la reserva!!!';
  END IF;
  IF NEW."Billing_date_to" IS NOT NULL THEN
    IF NEW."Billing_date_to" <= NEW."Billing_date_from" THEN
  --    RAISE exception '!!!Billing end date cannot be earlier than the start of the billing!!!Facturación hasta no puede ser anterior al inicio de la facturación!!!';
    END IF;
  END IF; 

  -- Next month
  IF NEW."Extra_type" = 'asap' THEN
    NEW."Billing_date_from" := NULL;
    NEW."Billing_date_to" := NULL;
  END IF;

  -- Fixed date
  IF NEW."Extra_type" = 'puntual' THEN
    IF NEW."Billing_date_from" IS NULL THEN
      RAISE exception '!!!Billing date is missing!!!Falta la fecha de facturación!!!';
    END IF;
    NEW."Billing_date_to" := NULL;
  END IF;

  -- Recurrent
  IF NEW."Extra_type" = 'recurrente' THEN
    IF NEW."Billing_date_from" IS NULL THEN
      RAISE exception '!!!Billing start date is missing!!!Falta la fecha de inicio facturación!!!';
    END IF;
    IF NEW."Billing_date_to" IS NULL THEN
      RAISE exception '!!!Billing end date is missing!!!Falta la fecha de fin facturación!!!';
    END IF;
  END IF;

  -- Product data
  SELECT "Tax_id", "Name", "Product_type_id"
  INTO tax_id, concept, product_type
  FROM "Billing"."Product" 
  WHERE id = NEW."Product_id";

  -- Provider
  IF NEW."Provider_id" IS NULL THEN
    IF product_type <> 3 THEN
      NEW."Provider_id" := 1;
    ELSE
      SELECT r."Owner_id" INTO owner_id FROM "Resource"."Resource" r WHERE r.id = resource_id;
      NEW."Provider_id" := owner_id;
    END IF;
  END IF;

  -- Tax
  IF NEW."Tax_id" IS NULL THEN
    NEW."Tax_id" := tax_id;
  END IF;

  -- Concept
  IF NEW."Concept" IS NULL THEN
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
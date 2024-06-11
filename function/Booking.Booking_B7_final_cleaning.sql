-- Final cleaning
DECLARE

  product_id INTEGER;
  tax_id INTEGER;
  payment_method_id INTEGER;

  curr_user VARCHAR;

BEGIN

  -- Final cleaning
  IF NEW."Date_from" >= '2024-06-01' AND NEW."Final_cleaning" > 0 THEN
    SELECT id, "Tax_id" into product_id, tax_id FROM "Billing"."Product" WHERE "Name" = 'Limpieza final';
    IF product_id IS NOT NULL THEN

      -- Superuser ROLE
      curr_user := CURRENT_USER;
      RESET ROLE; 

      SELECT "Payment_method_id" into payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Customer_id";
      IF NOT EXISTS (SELECT id FROM "Booking"."Booking_service" WHERE "Booking_id" = NEW.id AND "Product_id" = product_id) THEN
        INSERT INTO "Booking"."Booking_service" 
        ("Booking_id", "Billing_date_from", "Product_id", "Provider_id", "Concept", "Amount", "Tax_id", "Payment_method_id")
        VALUES (NEW.id, NEW."Date_from", product_id, 1, 'Limpieza final', NEW."Final_cleaning", tax_id, payment_method_id);
      END IF;

      -- Fin
      EXECUTE 'SET ROLE "' || curr_user || '"';

    END IF;
  END IF;
  RETURN NEW;

END;
-- Creación del pago
-- AFTER INSERT
BEGIN

	-- Envia email informando del nuevo pago
  IF NEW."Payment_type" = 'servicios' AND NEW."Payment_method_id" = 1 THEN
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'pago', NEW.id);
  END IF;
  RETURN NEW;

END;
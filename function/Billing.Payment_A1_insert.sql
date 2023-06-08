-- Creación del pago
-- AFTER INSERT
BEGIN

	-- Envia email informando del nuevo pago 
  INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'pago', NEW.id);
  RETURN NEW;

END;
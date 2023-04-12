-- Prepara la funcionalidad de pago por TPV
BEGIN

	IF pg_trigger_depth() > 1 THEN
		RETURN NEW;
	END IF;

	IF NEW."Payment_method_id" = 1 AND NEW."Payment_date" IS NULL THEN
		UPDATE "Billing"."Payment" 
		SET 
			"Pay" = CONCAT('https://dev.cotown.ciber.es/html/go/pay/1', NEW.id),
			"Order_num" = NULL,
			"Order_auth" = NULL
		WHERE id = NEW.id;
	ELSE
		UPDATE "Billing"."Payment" 
		SET "Pay" = ''
		WHERE id = NEW.id;
	END IF;

	RETURN NEW;

END;

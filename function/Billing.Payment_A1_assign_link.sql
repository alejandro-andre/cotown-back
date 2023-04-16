-- Asigna el link del boton para el pago por TPV
DECLARE

  pay VARCHAR = '';

BEGIN

  RESET ROLE; 

  IF NEW."Payment_method_id" = 1 AND NEW."Payment_date" IS NULL THEN
    pay := CONCAT('/functions/Auxiliar.goin?url=/admin/Billing.Pay/external?id=', NEW.id);
  END IF;

  IF COALESCE(NEW."Pay", '') <> pay THEN
    UPDATE "Billing"."Payment" SET "Pay" = pay WHERE id = NEW.id;
  END IF;

  RETURN NEW;

END;
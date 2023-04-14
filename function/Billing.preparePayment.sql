-- Prepara la funcionalidad de pago por TPV
DECLARE
  pay VARCHAR = '';

BEGIN
  IF NEW."Payment_method_id" = 1 AND NEW."Payment_date" IS NULL THEN
    pay := CONCAT('/functions/Auxiliar.go?url=/admin/Auxiliar.Segment/', NEW.id, '/view');
  END IF;

  IF COALESCE(NEW."Pay", '') <> pay THEN
    UPDATE "Billing"."Payment" SET "Pay" = pay WHERE id = NEW.id;
  END IF;

  RETURN NEW;
END;
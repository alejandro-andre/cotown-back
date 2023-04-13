-- Valida que la fecha de pago sea mayor que la fecha de emision, comentado para evitar errores con RedSys
BEGIN
  --IF NEW."Payment_date" IS NOT NULL THEN
  --  IF NEW."Payment_date" < NEW."Issued_date" THEN
  --    RAISE EXCEPTION '!!!The date of payment must be equal to or greater than the date of issue..!!!La fecha de pago debe ser igual o mayor a la fecha de emisión.!!!';
  --  END IF;
  --END IF;
  RETURN NEW;
END;

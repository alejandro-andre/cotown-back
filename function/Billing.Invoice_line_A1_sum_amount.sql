-- Calcula el importe de la factura, sumando sus líneas
-- AFTER INSERT/UPDATE/DELETE
DECLARE 

  total NUMERIC;
  invoice_id INTEGER;

BEGIN

  -- Invoice id
  IF TG_OP = 'DELETE' THEN
  	invoice_id = OLD."Invoice_id";
  ELSE
  	invoice_id = NEW."Invoice_id";
  END IF;

  -- Suma todas las líneas
  SELECT SUM("Amount")
  INTO total
  FROM "Billing"."Invoice_line"
  WHERE "Invoice_id" = invoice_id;

  -- Actualiza el importe
  UPDATE "Billing"."Invoice" 
  SET "Total" = total
  WHERE id = invoice_id;
 
  -- Return
  RETURN NEW; 

END;
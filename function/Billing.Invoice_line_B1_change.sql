-- Verifica si se puede modificar la factura
-- AFTER INSERT/UPDATE/DELETE
DECLARE 

  issued BOOLEAN;
  invoice_id INTEGER;

BEGIN

  -- Invoice id
  IF TG_OP = 'DELETE' THEN
  	invoice_id = OLD."Invoice_id";
  ELSE
  	invoice_id = NEW."Invoice_id";
  END IF;

  -- Issued?
  SELECT "Issued" INTO issued FROM "Billing"."Invoice" WHERE id = invoice_id;
  IF issued THEN
    RAISE EXCEPTION '!!!Bill has been already issued, cannot change!!!La factura ya ha sido emitida, no puede cambiarse!!!';
  END IF;

  -- Return
  RETURN NEW; 

END;
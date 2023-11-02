-- Verifica si se puede modificar la factura
-- AFTER INSERT/UPDATE/DELETE
DECLARE

  issued BOOLEAN;
  tax_id INTEGER;
  invoice_id INTEGER;
  concept VARCHAR;

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

  -- Tax
  IF NEW."Tax_id" IS NULL THEN
    SELECT "Tax_id" INTO tax_id FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Tax_id" := tax_id;
  END IF;

  -- Concept
  IF NEW."Concept" IS NULL THEN
    SELECT "Name" INTO concept FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Concept" := concept;
  END IF;

  -- Return
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  ELSE
    RETURN NEW;
  END IF;

END;
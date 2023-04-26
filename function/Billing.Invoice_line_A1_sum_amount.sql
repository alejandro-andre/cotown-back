-- Calcula el importe de la factura, sumando sus líneas
-- AFTER INSERT/UPDATE
DECLARE 

  total NUMERIC;

BEGIN

  RESET ROLE;
  
  -- Suma todas las líneas
  SELECT SUM("Amount")
  INTO total
  FROM "Billing"."Invoice_line"
  WHERE "Invoice_id"= NEW."Invoice_id";

  -- Actualiza el importe
  UPDATE "Billing"."Invoice" 
  SET "Total" = total
  WHERE id = NEW."Invoice_id";

  -- Return
  RETURN NEW; 

END;
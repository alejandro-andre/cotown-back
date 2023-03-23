-- Añade el importe a la factura
DECLARE 
	total NUMERIC;

BEGIN
	-- Sum all lines
	SELECT SUM("Amount")
	INTO total
	FROM "Billing"."Invoice_line"
	WHERE "Invoice_id"= NEW."Invoice_id";

	-- Update total on bill
	UPDATE "Billing"."Invoice" 
	SET "Total" = total
	WHERE id = NEW."Invoice_id";

	-- Return
	RETURN NEW; 
END;
-- Valida que las fechas de compra sea menor o igual a la fecha en curso y que la fecha de garnatia sea mayor que la fecha de compra
BEGIN

    IF NEW."Purchase_date" IS NOT NULL THEN
		IF NEW."Purchase_date" > current_date THEN
			RAISE EXCEPTION '!!!Date of purchase must be equal to or greater than today date.!!!La fecha de compra debe ser igual o menor al día de hoy.!!!';
		end  IF;
		IF NEW."Warranty_date" < NEW."Purchase_date"· THEN
			RAISE EXCEPTION '!!!The warranty date must be greater than the date of purchase.!!!La fecha de garantia debe ser mayor la fecha de compra.!!!';
		END IF;
	END IF;

	RETURN NEW;

END;
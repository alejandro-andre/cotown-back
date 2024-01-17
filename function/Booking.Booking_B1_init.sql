-- Inicializa la solicitud
DECLARE

  booking_fee_amount INTEGER;
  year INTEGER;

BEGIN

  -- Status por defecto
  IF NEW."Status" IS NULL THEN
    NEW."Status" := 'solicitud';
  END IF;

  -- Calcula el booking fee si está vacío
  IF NEW."Booking_fee_calc" IS NULL THEN

    -- Year
    year := EXTRACT(YEAR FROM NOW());
    IF EXTRACT(MONTH FROM NOW()) > 8 THEN
      year := year + 1;
    END IF; 

    -- Obtiene el valor del booking fee
    SELECT "Booking_fee"
    INTO booking_fee_amount
    FROM "Billing"."Pricing_detail" pd
    WHERE pd."Building_id" = NEW."Building_id"
    AND pd."Flat_type_id" = NEW."Flat_type_id"
    AND (pd."Place_type_id" = NEW."Place_type_id" OR NEW."Place_type_id" IS NULL)
    AND pd."Year" = year
    LIMIT 1;

    -- Asigna el valor obtenido
    NEW."Booking_fee_calc" := COALESCE(booking_fee_amount, 0);
    IF NEW."Booking_fee" IS NULL THEN
      NEW."Booking_fee" := NEW."Booking_fee_calc";
    END IF;

  END IF;

  -- Return
  RETURN NEW;

END;
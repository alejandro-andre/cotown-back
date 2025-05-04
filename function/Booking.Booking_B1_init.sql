-- Inicializa la solicitud
DECLARE

  booking_fee_amount INTEGER;
  year INTEGER;

  promotion RECORD;

BEGIN

  -- Status por defecto
  IF NEW."Status" IS NULL THEN
    NEW."Status" := 'solicitud';
  END IF;

  -- Look up promotion
  SELECT *
  INTO promotion
  FROM "Billing"."Promotion" p
  WHERE p."Building_id" = NEW."Building_id"
    AND (p."Flat_type_id" IS NULL OR p."Flat_type_id" = NEW."Flat_type_id")
    AND (p."Place_type_id" IS NULL OR p."Place_type_id" = NEW."Place_type_id")
    AND p."Date_from" <= NEW."Date_to" 
    AND p."Date_to" >= NEW."Date_from"
  ORDER BY id DESC
  LIMIT 1;
  NEW."Promotion_id" = promotion.id;

  -- Calcula el membership fee si está vacío
  IF NEW."Booking_fee_calc" IS NULL THEN

    -- Year
    year := EXTRACT(YEAR FROM NOW());
    IF EXTRACT(MONTH FROM NOW()) > 8 THEN
      year := year + 1;
    END IF; 

    -- Obtiene el valor del membership fee
    SELECT COALESCE("Booking_fee", 0)
    INTO booking_fee_amount
    FROM "Billing"."Pricing_detail" pd
    WHERE pd."Building_id" = NEW."Building_id"
      AND pd."Flat_type_id" = NEW."Flat_type_id"
      AND (pd."Place_type_id" = NEW."Place_type_id" OR NEW."Place_type_id" IS NULL)
      AND pd."Year" = year
    LIMIT 1;
    NEW."Booking_fee_calc" := booking_fee_amount;

    -- Asigna el valor obtenido con posible promoción
    IF NEW."Booking_fee" IS NULL THEN
      IF promotion."Value_fee" IS NOT NULL THEN
        booking_fee_amount := booking_fee_amount + promotion."Value_fee";
        NEW."Booking_discount_type_id" := 1;
      ELSE
        IF promotion."Value_fee_pct" IS NOT NULL THEN
          booking_fee_amount := booking_fee_amount * (1 + promotion."Value_fee_pct" / 100);
          NEW."Booking_discount_type_id" := 1;
        END IF;
      END IF;
      NEW."Booking_fee" := booking_fee_amount;
    END IF;

  END IF;

  -- Return
  RETURN NEW;

END;
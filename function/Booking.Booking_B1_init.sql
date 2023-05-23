-- Inicializa la solicitud
DECLARE

  booking_fee_amount INTEGER;

BEGIN

  -- Status por defecto
  IF NEW."Status" IS NULL THEN
    NEW."Status" := 'solicitud';
  END IF;

  -- Obtiene el valor del booking fee
  SELECT "Booking_fee" INTO booking_fee_amount FROM "Building"."Building" WHERE id = NEW."Building_id";
  NEW."Booking_fee" := booking_fee_amount;

  -- Return
  RETURN NEW;

END;
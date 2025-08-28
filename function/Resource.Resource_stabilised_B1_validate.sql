-- Valida stabilised ratios
-- BEFORE INSERT/UPDATE
BEGIN

  -- Ocupación
  IF NEW."Occupancy" > 100 THEN
    NEW."Occupancy" = 100;
  END IF;

  -- Ratios
  IF NEW."Rent_short" + NEW."Rent_medium" + NEW."Rent_long" > 100 THEN
      RAISE EXCEPTION '!!!Ratios cannot sum more than 100!!!Las ratios no pueden sumar mas de 100!!!';
  END IF;

  RETURN NEW;

END;
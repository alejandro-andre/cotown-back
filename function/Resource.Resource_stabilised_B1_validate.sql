-- Valida stabilised ratios
-- BEFORE INSERT/UPDATE
BEGIN

  -- Ocupación
  IF NEW."Occupancy" > 100 THEN
    NEW."Occupancy" = 100;
  END IF;

  -- Ratios
  IF NEW."Pct_short" + NEW."Pct_medium" + NEW."Pct_long" > 100 THEN
      RAISE EXCEPTION '!!!Ratios cannot sum more than 100!!!Las ratios no pueden sumar mas de 100!!!';
  END IF;

  RETURN NEW;

END;
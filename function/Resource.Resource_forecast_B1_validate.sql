-- Valida forecast ratios
-- BEFORE INSERT/UPDATE
BEGIN

  -- Fecha
  NEW."Date_price" := date_trunc('month', NEW."Date_price")::date;

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
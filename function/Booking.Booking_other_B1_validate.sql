-- Verifica los datos de la reserva
DECLARE

  pre_capex_diff DECIMAL;

BEGIN

  -- Dates
  IF NEW."Date_to" <= "Date_from" THEN
    RAISE EXCEPTION '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;
  IF NEW."Date_to" IS NOT NULL AND "Date_estimated" IS NULL THEN
    NEW."Date_estimated" = NEW."Date_to";
  END IF;

  -- Get pre-capex values
  SELECT COALESCE(r."Pre_capex_vacant", 0) - COALESCE(r."Pre_capex_long_term", 0)
  INTO pre_capex_diff
  FROM "Resource"."Resource" r
  WHERE r.id = NEW."Resource_id";

  -- Calc recommended contribution
  IF NEW."Contribution_recommended" IS NULL AND NEW."Contribution_percent" IS NOT NULL THEN
    NEW."Contribution_recommended" := COALESCE(NEW."Contribution_percent", 0) * pre_capex_diff / 100;
  END IF;

  -- Return record
  RETURN NEW;

END;
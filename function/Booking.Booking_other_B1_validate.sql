-- Verifica los datos de la reserva
DECLARE

  pre_capex_diff DECIMAL;

BEGIN

  -- Dates
  IF NEW."Date_to" <= NEW."Date_from" THEN
    RAISE EXCEPTION '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;
  IF NEW."Date_to" IS NOT NULL AND NEW."Date_estimated" IS NULL THEN
    NEW."Date_estimated" = NEW."Date_to";
  END IF;

  -- Auto Pre capex and Capes
  IF NEW."Date_estimated" IS NOT NULL AND NEW."Date_precapex" IS NULL AND NEW."Date_capex" IS NULL THEN
    NEW."Date_precapex" := (DATE_TRUNC('month', NEW."Date_estimated" + INTERVAL '2 months') + INTERVAL '1 month' - INTERVAL '1 day')::date;
    NEW."Date_capex" := (DATE_TRUNC('month', NEW."Date_precapex" + INTERVAL '4 months') + INTERVAL '1 month' - INTERVAL '1 day')::date;
  END IF;

  -- ITP Date
  IF NEW."Compensation_date" IS NOT NULL AND NEW."ITP_required_date" IS NULL THEN
    NEW."ITP_required_date" := NEW."Compensation_date" + INTERVAL '1 months';
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
-- Crea/Actualiza los bloqueos
DECLARE

  date_from DATE;

BEGIN

  -- Delete pre capex & capex locks
  DELETE 
  FROM "Resource"."Resource_availability" 
  WHERE "Resource_id" = NEW."Resource_id"
    AND "Status_id" IN (2, 3, 4);

  -- Long term
  IF NEW."Date_estimated" IS NULL THEN
	INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to")
  	VALUES (NEW."Resource_id", 2, NEW."Date_from", '2099/12/31');
    RETURN NEW;
  END IF;

  -- Fixed term
  INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to")
  VALUES (NEW."Resource_id", 2, NEW."Date_from", NEW."Date_estimated");
  date_from = NEW."Date_estimated" + INTERVAL '1 day';

  -- Add pre capex lock
  IF NEW."Date_precapex" IS NOT NULL THEN
    IF NEW."Date_precapex" <= date_from THEN
      RAISE EXCEPTION '!!!Pre capex end date is wrong!!!La fecha fin de pre capex es incorrecta!!!';
    END IF;
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to")
    VALUES (NEW."Resource_id", 3, date_from, NEW."Date_precapex");
    date_from = NEW."Date_precapex" + INTERVAL '1 day';
  END IF;

  -- Add capex lock
  IF NEW."Date_capex" IS NOT NULL THEN
    IF NEW."Date_capex" <= date_from THEN
      RAISE EXCEPTION '!!!Capex end date is wrong!!!La fecha fin de capex es incorrecta!!!';
    END IF;
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to")
    VALUES (NEW."Resource_id", 4, date_from, NEW."Date_capex");
  END IF;

  -- Return record
  RETURN NEW;

END;
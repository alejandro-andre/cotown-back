-- Crea/Actualiza los bloqueos
DECLARE

  curr_user VARCHAR;
  date_from DATE;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 

  -- Delete pre capex & capex locks
  DELETE 
  FROM "Resource"."Resource_availability" 
  WHERE "Resource_id" = NEW."Resource_id"
    AND "Status_id" IN (2, 3, 4);

  -- Return
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  END IF;

  -- Long term
  IF NEW."Date_estimated" IS NULL THEN
  	INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to", "Convertible")
    	VALUES (NEW."Resource_id", 2, NEW."Date_from", '2099/12/31', 'LTNC');
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- Fixed term
  IF NEW."Date_to" IS NULL THEN
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to", "Convertible")
    VALUES (NEW."Resource_id", 2, NEW."Date_from", NEW."Date_estimated", 'LTC');
  ELSE
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to", "Convertible")
    VALUES (NEW."Resource_id", 2, NEW."Date_from", NEW."Date_estimated", 'FTC');
  END IF;
  date_from = NEW."Date_estimated" + INTERVAL '1 day';

  -- Add pre capex lock
  IF NEW."Date_precapex" IS NOT NULL THEN
    IF NEW."Date_precapex" <= date_from THEN
      RAISE EXCEPTION '!!!Pre capex end date is wrong!!!La fecha fin de pre capex es incorrecta!!!';
    END IF;
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to", "Convertible")
    VALUES (NEW."Resource_id", 3, date_from, NEW."Date_precapex", 'PRECAPEX');
    date_from = NEW."Date_precapex" + INTERVAL '1 day';
  END IF;

  -- Add capex lock
  IF NEW."Date_capex" IS NOT NULL THEN
    IF NEW."Date_capex" <= date_from THEN
      RAISE EXCEPTION '!!!Capex end date is wrong!!!La fecha fin de capex es incorrecta!!!';
    END IF;
    INSERT INTO "Resource"."Resource_availability" ("Resource_id", "Status_id", "Date_from", "Date_to", "Convertible")
    VALUES (NEW."Resource_id", 4, date_from, NEW."Date_capex", 'CAPEX');
  END IF;

  -- Return record
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
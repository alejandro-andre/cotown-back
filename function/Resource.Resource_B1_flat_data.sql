-- Calcula y valida los campos del recurso
-- BEFORE INSERT/UPDATE
DECLARE

  code VARCHAR;
  curr_user VARCHAR;
  
BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Piso?
  IF NEW."Resource_type" = 'piso' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}$' THEN
      RAISE EXCEPTION '!!!Wrong flat code %, must have XXXnnn.nn.nn format!!!Código de piso % incorrecto, debe formato XXXnnn.nn.nn!!!', NEW."Code", NEW."Code";
    END IF;
    UPDATE "Resource"."Resource"
    SET
      "Building_id" = NEW."Building_id",
      "Owner_id" = NEW."Owner_id",
      "Service_id" = NEW."Service_id",
      "Billing_type" = NEW."Billing_type",
      "Sale_type" = NEW."Sale_type",
      "Management_fee" = NEW."Management_fee"
    WHERE "Flat_id" = NEW.id 
      AND id <> NEW.id;
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- Habitacion
  IF NEW."Resource_type" = 'habitacion' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}\.H\d{2}$' THEN
      EXECUTE 'SET ROLE "' || curr_user || '"';
      RAISE EXCEPTION '!!!Wrong room code %, must have XXXnnn.nn.nn.Hnn format!!!Código de habitacion %, incorrecto, debe formato XXXnnn.nn.nn.Hnn!!!', NEW."Code", NEW."Code";
    END IF;
  END IF;

-- Plaza
  IF NEW."Resource_type" = 'plaza' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}\.H\d{2}\.P\d$' THEN
      EXECUTE 'SET ROLE "' || curr_user || '"';
      RAISE EXCEPTION '!!!Wrong place code %, must have XXXnnn.nn.nn.Hnn.Pn format!!!Código de plaza % incorrecto, debe formato XXXnnn.nn.nn.Hnn.Pn!!!', NEW."Code", NEW."Code";
    END IF;
  	SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Room_id";
  END IF;

  -- Valida el codigo del recurso
  IF code <> SUBSTRING(NEW."Code", 1, LENGTH(code)) THEN
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RAISE EXCEPTION '%', CONCAT('!!!Wrong resource code, must start with ', code, '!!!Código de recurso incorrecto, debe comenzar por ', code, '!!!');
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;

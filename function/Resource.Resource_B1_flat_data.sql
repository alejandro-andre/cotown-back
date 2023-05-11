---- Calcula y valida los campos del recurso
-- BEFORE INSERT/UPDATE
DECLARE

  reg RECORD;
  code VARCHAR;
 
BEGIN

  -- Piso?
  IF NEW."Resource_type" = 'piso' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}$' THEN
      RAISE EXCEPTION '!!!Wrong flat code', NEW."Code", ', must have XXXnnn.nn.nn format!!!Código de piso ', NEW."Code", ' incorrecto, debe formato XXXnnn.nn.nn!!!';
    END IF;
    UPDATE "Resource"."Resource" SET id=id WHERE "Flat_id" = NEW.id;
    RETURN NEW;
  END IF;

  -- Lee el piso al que pertenece
  SELECT * INTO reg FROM "Resource"."Resource" WHERE id = NEW."Flat_id";

  -- Habitacion
  IF NEW."Resource_type" = 'habitacion' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}\.H\d{2}$' THEN
      RAISE EXCEPTION '!!!Wrong room code', NEW."Code", ', must have XXXnnn.nn.nn.Hnn format!!!Código de habitacion ', NEW."Code", ' incorrecto, debe formato XXXnnn.nn.nn.Hnn!!!';
    END IF;
  END IF;

 -- Plaza
  IF NEW."Resource_type" = 'plaza' THEN
    IF NOT NEW."Code" ~ '^[A-Z]{3}\w{3}\.\w{2}\.\w{2}\.H\d{2}\.P\d$' THEN
      RAISE EXCEPTION '!!!Wrong place code ', NEW."Code", ', must have XXXnnn.nn.nn.Hnn.Pn format!!!Código de plaza ', NEW."Code", ' incorrecto, debe formato XXXnnn.nn.nn.Hnn.Pn!!!';
    END IF;
  	SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Room_id";
  END IF;

  -- Valida el codigo del recurso
  IF code <> SUBSTRING(NEW."Code", 1, LENGTH(code)) THEN
    RAISE EXCEPTION '%', CONCAT('!!!Wrong resource code, must start with ', code, '!!!Código de recurso incorrecto, debe comenzar por ', code, '!!!');
  END IF;

  -- Asigna los datos
  NEW."Building_id" := reg."Building_id";
  NEW."Flat_type_id" := reg."Flat_type_id";
  NEW."Owner_id" := reg."Owner_id";
  NEW."Service_id" := reg."Service_id";
  NEW."Billing_type" := reg."Billing_type";
  NEW."Sale_type" := reg."Sale_type";
 
  -- Return
  RETURN NEW;

END;
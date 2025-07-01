-- Calcula las partes de un piso que supone una plaza o habitación
-- AFTER INSERT/DELETE
DECLARE

  reg RECORD;
  num INTEGER;
  parts INTEGER;
  flat_id INTEGER;
  res VARCHAR;

BEGIN

  IF pg_trigger_depth() = 1 THEN
 
    -- Flat id
    IF TG_OP = 'DELETE' THEN
    	flat_id = OLD."Flat_id";
    ELSE
    	flat_id = NEW."Flat_id";
    END IF;
  
    -- Cuenta las partes totales del piso
    SELECT COUNT("Flat_id") - COUNT("Room_id") / 2
    INTO parts
    FROM "Resource"."Resource"
    WHERE "Flat_id" = flat_id;
 
    -- Recorre todos los recursos del piso
    FOR reg IN
      SELECT id, "Code", "Room_id", "Description"
      FROM "Resource"."Resource"
      WHERE "Flat_id" = flat_id
      FOR UPDATE
    LOOP
      SELECT count(*)
      INTO num
      FROM "Resource"."Resource"
      WHERE "Room_id" = reg.id;
      IF num = 0 THEN
        UPDATE "Resource"."Resource" SET "Part" = CONCAT('1/', parts) WHERE id=reg.id;
      ELSE
        UPDATE "Resource"."Resource" SET "Part" = CONCAT('2/', parts) WHERE id=reg.id;
      END IF;
    END LOOP;

  END IF;

  -- Return
  RETURN NEW;

END;

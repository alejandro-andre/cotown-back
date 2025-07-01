-- Actualiza el código de los recursos de un edificio
BEGIN
	
  -- Solo si ha cambiado el código
  IF NEW."Code" <> OLD."Code" THEN

    -- Primero las habitaciones y plazas
    UPDATE "Resource"."Resource"
    SET "Code" = concat(NEW."Code", substring("Code", 7, 999))
    WHERE "Building_id" = NEW.id
    AND "Resource_type" <> 'piso';

    -- Luego el piso
    UPDATE "Resource"."Resource"
    SET "Code" = concat(NEW."Code", substring("Code", 7, 999))
    WHERE "Building_id" = NEW.id
    AND "Resource_type" = 'piso';

  END IF;

  -- Return record
  RETURN NEW;

END;
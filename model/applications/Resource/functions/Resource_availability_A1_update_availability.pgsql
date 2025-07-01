-- Almacena los bloqueos de un piso en tabla auxiliar
-- AFTER INSERT/UPDATE/DELETE
DECLARE

  code VARCHAR;
  curr_user VARCHAR;
  reg RECORD;
  cur CURSOR FOR
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');
  status VARCHAR;
  not_flat BOOL;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;
 
  -- Borra todos las reservas relacionadas con ese bloqueo
  IF TG_OP = 'DELETE' THEN
    DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = OLD.id;
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN OLD;
  ELSE
    DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = NEW.id;
  END IF;

  -- Obtiene el código del recurso
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

  -- Lee el status
  SELECT "Name", "Not_flat" INTO status, not_flat FROM "Resource"."Resource_status" WHERE id = NEW."Status_id";

  -- Abre el cursor
  OPEN cur;
  FETCH cur INTO reg;
  WHILE (FOUND) LOOP
 
    -- Bloqueos solo para habitaciones
    IF not_flat AND reg."Resource_type" = 'piso' THEN
    ELSE

      -- Inserta los bloqueos de la no disponibilidad
      INSERT INTO "Booking"."Booking_detail" (
        "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id",
        "Status", "Date_from", "Date_to", "Lock"
      )
      VALUES (
        NEW.id, NULL, NULL, NULL, reg.id, reg."Building_id",
        status, NEW."Date_from", NEW."Date_to", TRUE
      );

    END IF;

	-- Siguiente
    FETCH cur INTO reg;

  END LOOP;
  CLOSE cur;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
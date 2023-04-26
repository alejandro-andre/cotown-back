-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  reg RECORD;
  cur CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

BEGIN

  RESET ROLE;
  
  -- Borra todos los registros relacionados con ese bloqueo
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_id" = NEW.id;
  IF NEW."Resource_id" IS NULL THEN
    RETURN NEW;
  END IF;
  
  -- Obtiene el código del recurso
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

  -- Abre el cursor
  OPEN cur;

  -- Siguiente registro
  FETCH cur INTO reg;

  -- Recorre todos los padres e hijos del recurso
  WHILE (FOUND) LOOP
  
    -- Inserta la reserva
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NULL, NEW.id, NULL, NULL, reg.id, reg."Building_id", reg."Flat_type_id", reg."Place_type_id",
      reg."Resource_type", NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN reg.id = NEW."Resource_id" THEN FALSE ELSE TRUE END)
    );


    -- Siguiente registro
     FETCH cur INTO reg;
  
  END LOOP;

  -- Cierra el cursor
  CLOSE cur;
  
  -- Return
  RETURN NEW;

END;
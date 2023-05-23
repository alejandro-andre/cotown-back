-- Almacena los bloqueos de un piso en tabla auxiliar
-- AFTER INSERT/UPDATE
DECLARE

  status VARCHAR;

  re RECORD;
  res CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Flat_id" = NEW."Resource_id"
    OR id = NEW."Resource_id";

BEGIN

  --RESET ROLE;

  -- Borra todos las reservas relacionadas con ese bloqueo
  DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = NEW.id;

  -- Lee el status
  SELECT "Name" INTO status FROM "Resource"."Resource_status" WHERE id = NEW."Status_id";

  -- Abre el cursor
  OPEN res;
  FETCH res INTO re;
  WHILE (FOUND) LOOP
  
    -- Inserta el bloqueo
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NEW.id, NULL, NULL, NULL, re.id, re."Building_id", re."Flat_type_id", re."Place_type_id",
      re."Resource_type", status, NEW."Date_from", NEW."Date_to", TRUE
    );

     FETCH res INTO re;
  END LOOP;
  CLOSE res;

  -- Return
  RETURN NEW;

END;

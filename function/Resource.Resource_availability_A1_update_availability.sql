-- Almacena los bloqueos de un piso en tabla auxiliar
DECLARE

  status VARCHAR;
  reg RECORD;
  cur CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Flat_id" = NEW."Resource_id";

BEGIN

  RESET ROLE;

  -- Delete all records related to that lock
  DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = NEW.id;

  -- Get statusdata
  SELECT "Name" INTO status FROM "Resource"."Resource_status" WHERE id = NEW."Status_id";

  -- Open cursor
  OPEN cur;

  -- Next record
  FETCH cur INTO reg;

  -- Loop thru all parents and children
  WHILE (FOUND) LOOP
  
    -- Insert booking
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_rooming_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NEW.id, NULL, NULL, reg.id, reg."Building_id", reg."Flat_type_id", reg."Place_type_id",
      reg."Resource_type", status, NEW."Date_from", NEW."Date_to", TRUE
    );

    -- Next record
     FETCH cur INTO reg;
  
  END LOOP;

  -- Return
  RETURN NEW;

END;
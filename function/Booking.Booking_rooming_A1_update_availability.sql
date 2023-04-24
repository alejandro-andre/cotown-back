-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  reg RECORD;
  booking RECORD;
  cur CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

BEGIN

  RESET ROLE;
  
  -- Delete all records related to that lock
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_rooming_id" = NEW.id;
  IF NEW."Resource_id" IS NULL THEN
    RETURN NEW;
  END IF;
  
  -- Get booking
  SELECT * INTO booking FROM "Booking"."Booking_group" WHERE id = NEW."Booking_id";

  -- Get resource code
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

  -- Open cursor
  OPEN cur;

  -- Next record
  FETCH cur INTO reg;

  -- Loop thru all parents and children
  WHILE (FOUND) LOOP
  
    -- Insert booking
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NULL, NULL, NEW."Booking_id", NEW.id, reg.id, reg."Building_id", reg."Flat_type_id", reg."Place_type_id",
      reg."Resource_type", 'grupo', booking."Date_from", booking."Date_to", (CASE WHEN reg.id = NEW."Resource_id" THEN FALSE ELSE TRUE END)
    );

    -- Next record
     FETCH cur INTO reg;
  
  END LOOP;

  -- Close cursor
  CLOSE cur;
  
  -- Return
  RETURN NEW;

END;
-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  
  re RECORD;
  res CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

BEGIN

  RESET ROLE;
  
  -- Delete all records related to that room
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_rooming_id" = NEW.id;
  
  -- Get resource code
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

  -- Open resource cursor
  OPEN res;
  FETCH res INTO re;
  WHILE (FOUND) LOOP
  
    -- Insert booking
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NULL, NULL, NEW."Booking_id", NEW.id, re.id, re."Building_id", re."Flat_type_id", re."Place_type_id",
      re."Resource_type", NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN re.id = room."Resource_id" THEN FALSE ELSE TRUE END)
    );

    FETCH res INTO re;
  END LOOP;
  CLOSE res;

  -- Return
  RETURN NEW;

END;

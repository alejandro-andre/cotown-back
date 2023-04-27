-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  
  room RECORD;
  rooms CURSOR FOR 
    SELECT *
    FROM "Booking"."Booking_rooming"
    WHERE "Booking_id" = NEW.id;

  re RECORD;
  res CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

BEGIN

  RESET ROLE;
  
  -- Delete all records related to that group
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_group_id" = NEW.id;
  
  -- Open rooming cursor
  OPEN rooms;
  FETCH rooms INTO room;
  WHILE (FOUND) LOOP

	  -- Get resource code
  	SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = room."Resource_id";
  
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
        NULL, NULL, room."Booking_id", room.id, re.id, re."Building_id", re."Flat_type_id", re."Place_type_id",
        re."Resource_type", NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN re.id = room."Resource_id" THEN FALSE ELSE TRUE END)
      );

      FETCH res INTO re;
    END LOOP;
    CLOSE res;


    FETCH rooms INTO room;
  END LOOP;
  CLOSE rooms;
  
  -- Return
  RETURN NEW;

END;

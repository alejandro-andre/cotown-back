-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  reg RECORD;
  cur CURSOR FOR 
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

-- Actualiza la tabla auxiliar de disponibilidades
BEGIN

  -- Delete all records related to that lock
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_id" = NEW.id;
  IF NEW."Resource_id" IS NULL THEN
    RETURN NEW;
  END IF;
  
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
      "Availability_id", "Booking_id", "Resource_id", "Building_id", "Flat_type_id", "Place_type_id",
      "Resource_type", "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NULL, NEW.id, reg.id, reg."Building_id", reg."Flat_type_id", reg."Place_type_id",
      reg."Resource_type", NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN reg.id = NEW."Resource_id" THEN FALSE ELSE TRUE END)
    );


    -- Next record
     FETCH cur INTO reg;
  
  END LOOP;

  -- Close cursor
  CLOSE cur;
  
  -- Return
  RETURN NEW;

END;
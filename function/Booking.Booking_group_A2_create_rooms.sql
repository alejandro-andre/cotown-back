-- Crea/Actualiza la rooming list
DECLARE

  rec_id INTEGER;
  room_id INTEGER;
  room_ids INTEGER[];
  room_code VARCHAR;

  re RECORD;
  res CURSOR FOR
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(room_code, '%')
    OR room_code LIKE CONCAT("Code", '%');

BEGIN

  -- No changes
  IF OLD."Room_ids"  = NEW."Room_ids" AND
     OLD."Date_from" = NEW."Date_from" AND
     OLD."Date_to"   = NEW."Date_to" THEN
    RETURN NEW;
  END IF;

  -- Get place ids from codes
  RESET ROLE;
  SELECT array_agg(id) INTO room_ids FROM "Resource"."Resource" WHERE "Code" = ANY(NEW."Room_ids");

  -- Delete ALL locks
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_group_id" = NEW.id;

  -- No rooms
  IF room_ids IS NULL THEN
    DELETE FROM "Booking"."Booking_group_rooming" WHERE "Booking_id" = NEW.id;
    DELETE FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id;
    RETURN NEW;
  END IF;

  -- Delete removed rooms
  DELETE FROM "Booking"."Booking_group_rooming" WHERE "Room_id" IN (SELECT id FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id AND "Resource_id" <> ALL(room_ids));
  DELETE FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id AND "Resource_id" <> ALL(room_ids);

  -- Insert new rooms
  FOREACH room_id IN ARRAY(room_ids) LOOP

    -- Select room code
    SELECT "Code" INTO room_code FROM "Resource"."Resource" WHERE id = room_id;

    -- Upsert room
    SELECT bgr.id 
	INTO rec_id 
	FROM "Booking"."Booking_group_rooms" bgr 
	WHERE bgr."Resource_id" = room_id AND bgr."Booking_id" = NEW.id;
	IF rec_id IS NULL THEN
      INSERT
        INTO "Booking"."Booking_group_rooms" ("Booking_id", "Resource_id", "Code")
        VALUES (NEW.id, room_id, room_code)
        RETURNING id INTO rec_id;
	END IF;

    -- Locks
    IF NEW."Status" NOT IN ('cancelada') THEN
      OPEN res;
      FETCH res INTO re;
      WHILE (FOUND) LOOP
        INSERT INTO "Booking"."Booking_detail" (
          "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id",
          "Status", "Date_from", "Date_to", "Lock", "Booked_resource_id", 
          "Billing_type", "Billing_type_last"
        )
        VALUES (
          NULL, NULL, NEW.id, NULL, re.id, re."Building_id",
          NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN re.id = room_id THEN FALSE ELSE TRUE END), room_id,
          NEW."Billing_type", NEW."Billing_type_last"
        );
        FETCH res INTO re;
      END LOOP;
      CLOSE res;
    END IF;

  END LOOP;

  -- Return record
  RETURN NEW;

END;
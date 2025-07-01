-- Crea/Actualiza la rooming list
DECLARE

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

  -- Update rooming list if status changed
  --?Remove
  IF OLD."Status" <> NEW."Status" THEN
    UPDATE "Booking"."Booking_group_rooming" SET id = id WHERE "Booking_id" = NEW.id;
  END IF;
  
  -- No changes
  --IF OLD."Room_ids" = NEW."Room_ids" THEN
  --  RETURN NEW;
  --END IF;

  -- Get place ids from codes
  RESET ROLE;
  SELECT array_agg(id) INTO room_ids FROM "Resource"."Resource" WHERE "Code" = ANY(NEW."Room_ids");

  -- No rooms
  IF room_ids IS NULL THEN
    DELETE FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id;
    DELETE FROM "Booking"."Booking_group_rooming" WHERE "Booking_id" = NEW.id;
    DELETE FROM "Booking"."Booking_detail" WHERE "Booking_group_id" = NEW.id;
    RETURN NEW;
  END IF;

  -- Delete locks and removed rooms
  DELETE FROM "Booking"."Booking_group_rooms" WHERE "Booking_id" = NEW.id;
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_group_id" = NEW.id;
  DELETE FROM "Booking"."Booking_group_rooming" WHERE "Booking_id" = NEW.id AND "Resource_id" <> ALL(room_ids);

  -- Insert new rooms
  FOREACH room_id IN ARRAY(room_ids) LOOP

    -- Code
    SELECT "Code" INTO room_code FROM "Resource"."Resource" WHERE id = room_id;

    -- Expand rooms
    INSERT
      INTO "Booking"."Booking_group_rooms" ("Booking_id", "Resource_id", "Code")
      VALUES (NEW.id, room_id, room_code);

    -- Rooming list
    INSERT
      INTO "Booking"."Booking_group_rooming" ("Booking_id", "Resource_id", "Check_in", "Check_out")
      VALUES (NEW.id, room_id, NEW."Date_from", NEW."Date_to")
    ON CONFLICT ("Booking_id", "Resource_id", "Check_in") DO NOTHING;

    -- Locks
    IF NEW."Status" NOT IN ('cancelada') THEN
      OPEN res;
      FETCH res INTO re;
      WHILE (FOUND) LOOP
        INSERT INTO "Booking"."Booking_detail" (
          "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id",
          "Status", "Date_from", "Date_to", "Lock", "Booked_resource_id", "Billing_type", "Billing_type_last"
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
-- Crea/Actualiza la rooming list
DECLARE

  room_id INTEGER;
  room_ids INTEGER[];

BEGIN

  -- No changes
  IF OLD."Room_ids" = NEW."Room_ids" THEN
    RETURN NEW;
  END IF;

  -- Get place ids
  SELECT array_agg(id) INTO room_ids FROM "Resource"."Resource" WHERE "Code" = ANY(NEW."Room_ids");

  -- Updates rooms in the list
  RESET ROLE;
  IF room_ids IS NOT NULL THEN
    DELETE FROM "Booking"."Booking_rooming" WHERE "Booking_id" = NEW.id AND "Resource_id" <> ALL(room_ids);
    FOREACH room_id IN ARRAY(room_ids) LOOP
      INSERT
        INTO "Booking"."Booking_rooming" ("Booking_id", "Resource_id", "Check_in", "Check_out")
        VALUES (NEW.id, room_id, NEW."Date_from", NEW."Date_to")
      ON CONFLICT ("Booking_id", "Resource_id") DO NOTHING;
    END LOOP;
  ELSE
    DELETE FROM "Booking"."Booking_rooming" WHERE "Booking_id" = NEW.id;
  END IF;

  -- Return record
  RETURN NEW;

END;
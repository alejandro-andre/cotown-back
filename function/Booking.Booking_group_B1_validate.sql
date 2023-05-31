-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;

  room_id INTEGER;
  room_ids INTEGER[];

BEGIN
 
  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;

  -- Check the places
  IF (NEW."Rooms" IS NULL OR NEW."Rooms" < 1) THEN
    RAISE exception '!!!Enter the number of places!!!Introduzca el número de plazas!!!';
  END IF;

  -- Check the Rent is not null
  IF (NEW."Rent" IS NULL ) THEN
    RAISE exception '!!!Enter the amount of rent!!!Introduzca el importe de la renta!!!';
  END IF;

  -- Check the Services is not null
  IF (NEW."Services" IS NULL ) THEN
    RAISE exception '!!!Enter the services of rent!!!Introduzca el importe de los servicios!!!';
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Get place ids
  SELECT array_agg(id) INTO room_ids FROM "Resource"."Resource" WHERE "Code" = ANY(NEW."Room_ids");
 
  -- Delete rooms not in the list
  DELETE FROM "Booking"."Booking_rooming" WHERE "Booking_id" = NEW.id AND "Resource_id" <> ALL(room_ids);
 
  -- Create rooms in the list
  IF room_ids IS NOT NULL THEN
    FOREACH room_id IN ARRAY(room_ids) LOOP
      INSERT INTO "Booking"."Booking_rooming" ("Booking_id", "Resource_id") VALUES (NEW.id, room_id)
      ON CONFLICT ("Booking_id", "Resource_id") DO NOTHING;
    END LOOP;
  END IF;

  -- Return record
  RETURN NEW;

END;
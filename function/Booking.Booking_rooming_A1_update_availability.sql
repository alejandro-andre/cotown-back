-- Almacena las reservas en tabla auxiliar
DECLARE

  code VARCHAR;
  curr_user VARCHAR;
  booking RECORD;
  re RECORD;
  res CURSOR FOR
    SELECT *
    FROM "Resource"."Resource"
    WHERE "Code" LIKE CONCAT(code, '%')
    OR code LIKE CONCAT("Code", '%');

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;
 
  -- Borra todas reservas de esa plaza
  IF TG_OP = 'DELETE' THEN
    DELETE FROM "Booking"."Booking_detail" WHERE "Booking_rooming_id" = NEW.id;
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN OLD;
  END IF;
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_rooming_id" = NEW.id;
  IF NEW."Resource_id" IS NULL THEN
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- Obtiene la reserva padre/grupo
  SELECT * INTO booking FROM "Booking"."Booking_group" WHERE id = NEW."Booking_id";

  -- Obtiene el código de la plaza
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

  -- Recorre todos los recursos padres e hijos de la plaza
  OPEN res;
  FETCH res INTO re;
  WHILE (FOUND) LOOP
 
    -- Inserta bloqueo
    INSERT INTO "Booking"."Booking_detail" (
      "Availability_id", "Booking_id", "Booking_group_id", "Booking_rooming_id", "Resource_id", "Building_id",
      "Status", "Date_from", "Date_to", "Lock"
    )
    VALUES (
      NULL, NULL, NEW."Booking_id", NEW.id, re.id, re."Building_id",
      booking."Status", booking."Date_from", booking."Date_to", (CASE WHEN re.id = NEW."Resource_id" THEN FALSE ELSE TRUE END)
    );

    FETCH res INTO re;
  END LOOP;
  CLOSE res;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;

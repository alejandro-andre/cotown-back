-- Actualizacion de status
DECLARE

  bg_status "Auxiliar"."Group_status";
  status "Auxiliar"."Rooming_status";

BEGIN

  -- Booking status
  SELECT "Status"
  INTO bg_status
  FROM "Booking"."Booking_group"
  WHERE id = NEW."Booking_id";
  IF bg_status != 'inhouse' THEN
    RETURN NEW;
  END IF;

  -- Rooming status
  status := NEW."Status";

  -- Checkin
  IF status IS NULL THEN
    IF NEW."Check_in" <= CURRENT_DATE THEN
      status = 'checkin';
    END IF;
  END IF;

  -- Inhouse
  IF status = 'checkin' THEN
    IF NEW."Check_in_ok" THEN
      status = 'inhouse';
    END IF;
  END IF;

  -- Checkout
  IF status = 'inhouse' THEN
    IF NEW."Check_out" <= CURRENT_DATE THEN
      status = 'checkout';
    ELSE
      IF NOT NEW."Check_in_ok" THEN
        status = 'checkin';
      END IF;
    END IF;
  END IF;

  -- Revised
  IF status = 'checkout' THEN
    IF NEW."Revision_ok" THEN
      status = 'revisada';
    END IF;
  END IF;

  -- Update status
  IF status <> NEW."Status" OR (status IS NOT NULL AND NEW."Status" IS NULL) THEN
    NEW."Status" = status;
  END IF;

  -- Return record
  RETURN NEW;
  
END;
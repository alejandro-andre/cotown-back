-- Borra los bloqueos
BEGIN

  RESET ROLE;

  -- Delete all records related to that lock
  DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = OLD.id;
  RETURN OLD;

END;
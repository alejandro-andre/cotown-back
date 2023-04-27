-- Borra los bloqueos
-- AFTER DELETE
BEGIN

  RESET ROLE;
  DELETE FROM "Booking"."Booking_detail" WHERE "Availability_id" = OLD.id;
  RETURN OLD;

END;
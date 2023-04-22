-- Borra las reservas de la tabla auxiliar
BEGIN

  RESET ROLE;
  
  -- Delete all records related to that lock
  DELETE FROM "Booking"."Booking_detail" WHERE "Booking_rooming_id" = OLD.id;
  RETURN OLD;

END;
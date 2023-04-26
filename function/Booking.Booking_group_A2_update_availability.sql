-- Update rooming info
BEGIN

  RESET ROLE; 
  UPDATE "Booking"."Booking_rooming" SET id=id WHERE "Booking_id" = NEW.id;
  RETURN NEW;

END;
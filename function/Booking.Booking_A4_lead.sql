-- Encola la reserva para su envío al CRM (Pipedrive)
-- AFTER INSERT
DECLARE

  curr_user VARCHAR;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Encola el alta. El batch_sendcrm la procesa y marca "Sent_at"
  INSERT INTO "Booking"."Booking_lead" ("Booking_id", "Event")
    VALUES (NEW.id, 'alta')
    ON CONFLICT ("Booking_id", "Event") DO NOTHING;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;

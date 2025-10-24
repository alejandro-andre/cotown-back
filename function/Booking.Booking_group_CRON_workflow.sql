-- Actualizacion de status
DECLARE

BEGIN

  -- In house
  BEGIN
    UPDATE "Booking"."Booking_group" b
    SET "Status" = 'inhouse'
    WHERE b."Status" = 'grupoconfirmado'
    AND b."Date_from" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "inhouse": % %', SQLSTATE, SQLERRM;
  END; 
 
  -- Revision
  BEGIN
    UPDATE "Booking"."Booking_group" b
    SET "Status" = 'revision'
    WHERE b."Status" = 'inhouse'
    AND b."Date_to" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "revision": % %', SQLSTATE, SQLERRM;
  END; 
 
END;
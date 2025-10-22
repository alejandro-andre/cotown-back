-- Actualizacion planificada de status
DECLARE

BEGIN

  -- NULL to checkin
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" b
    SET "Status" = 'checkin'
    WHERE b."Status" IS NULL
    AND b."Check_in" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-in": % %', SQLSTATE, SQLERRM;
  END; 

  -- inhouse to checkout
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" b
    SET "Status" = 'checkout'
    WHERE b."Status" = 'inhouse'
    AND b."Check_out" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-out": % %', SQLSTATE, SQLERRM;
  END; 

END;
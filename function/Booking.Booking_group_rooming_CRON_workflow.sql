-- Actualizacion planificada de status
DECLARE

BEGIN

  -- NULL to checkin
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'checkin'
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" = 'inhouse'
      AND br."Status" IS NULL AND br."Check_in" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-in": % %', SQLSTATE, SQLERRM;
  END; 

  -- inhouse to checkout
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'checkout'
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" = 'inhouse'
      AND br."Status" = 'inhouse' AND br."Check_out" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-out": % %', SQLSTATE, SQLERRM;
  END; 

END;
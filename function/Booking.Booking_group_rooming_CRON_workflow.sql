-- Actualizacion planificada de status
DECLARE

BEGIN

  -- to checkin
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'checkin'
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" = 'inhouse'
      AND b."Type_B2C" AND br."Status" IS NULL AND br."Check_in" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-in": % %', SQLSTATE, SQLERRM;
  END; 

  -- to inhouse
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'inhouse', "Check_in_ok" = TRUE
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" = 'inhouse'
      AND NOT b."Type_B2C" AND (br."Status" IS NULL OR br."Status" = 'checkin') AND br."Check_in" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "in-house": % %', SQLSTATE, SQLERRM;
  END; 

  -- to checkout
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'checkout'
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" = 'inhouse'
      AND b."Type_B2C" AND br."Status" IN ('checkin', 'inhouse') AND br."Check_out" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "check-out": % %', SQLSTATE, SQLERRM;
  END; 

  -- to revisada
  BEGIN
    UPDATE "Booking"."Booking_group_rooming" br
    SET "Status" = 'revisada', "Check_out_revision_ok" = TRUE
    FROM "Booking"."Booking_group" b
    WHERE b.id = br."Booking_id" AND b."Status" IN ('inhouse', 'revision')
      AND NOT b."Type_B2C" AND br."Status" IN ('checkin', 'inhouse', 'checkout') AND br."Check_out" <= CURRENT_DATE;
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error actualizando reserva B2B a "revisada": % %', SQLSTATE, SQLERRM;
  END; 

END;
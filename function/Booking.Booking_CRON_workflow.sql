-- Actualizacion planificada de status
DECLARE

  rec RECORD;

BEGIN

  RESET ROLE;

  -- Caduca las solicitudes pendientes de pago pasadas de fecha
  BEGIN
    UPDATE "Booking"."Booking"
    SET "Status"='caducada'
    WHERE "Booking"."Expiry_date" < CURRENT_DATE
    AND "Booking"."Status"='pendientepago';
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error caducando solicitudes pasadas de fecha: % %', SQLSTATE, SQLERRM;
  END; 

  -- Actualiza el estado a 'descartada' de todas las solicitudes que esten caducadas con la fecha de caducidad a NULL o
  -- con la fecha de caducidad 5 dias menor que la fecha en curso.
  BEGIN
    UPDATE "Booking"."Booking"
    SET "Status"='descartada'
    WHERE "Booking"."Status"='caducada'
    AND ("Booking"."Expiry_date" IS NULL OR "Booking"."Expiry_date" < (CURRENT_DATE + INTERVAL '5 days'));
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error descartando solicitudes caducadas: % %', SQLSTATE, SQLERRM;
  END; 

  -- Actualiza el estado a 'descartada' de todas las solicitudes que no hayan pagado el deposito y falte menos de un
  -- mes para la fecha de entrada, con periodo de gracia de 48h desde la creación del pago
  BEGIN
    UPDATE "Booking"."Booking" b
    SET "Status" = 'descartadapagada'
    WHERE b."Status" = 'confirmada'
    AND b."Date_from" < (CURRENT_DATE + INTERVAL '30 days')
    AND EXISTS (
      SELECT id
      FROM "Billing"."Payment" p
      WHERE p."Booking_id" = b.id
      AND p."Payment_type" = 'deposito'
      AND p."Issued_date" < (CURRENT_DATE - INTERVAL '4 days')
    );
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error descartando solicitudes que no pagan deposito: % %', SQLSTATE, SQLERRM;
  END; 

  -- Actualiza el estado a 'check_in' de todas las reservas que tienen que entrar en el dia en curso
  BEGIN
    FOR rec IN
      SELECT * FROM "Booking"."Booking"
      WHERE CURRENT_DATE >= COALESCE("Check_in", "Date_from")
      AND ("Status" = 'checkinconfirmado' OR "Status" = 'contrato')
    LOOP
      BEGIN
        UPDATE "Booking"."Booking"
        SET "Status" = 'checkin'
        WHERE id = rec.id;
      EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error en check-in %: % %', rec.id, SQLSTATE, SQLERRM;
      END;
    END LOOP;
  END;  

  -- Actualiza el estado a 'check_out' de todas las reservas que tienen que salir en el dia en curso
  BEGIN
    UPDATE "Booking"."Booking"
    SET "Status"='checkout'
    WHERE CURRENT_DATE >= COALESCE("Booking"."Check_out", "Booking"."Date_to")
    AND "Booking"."Status"='inhouse';
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error en check-out: % %', SQLSTATE, SQLERRM;
  END; 

  -- Borra cuestionarios no completados, siete dias despues
  BEGIN
    DELETE FROM "Booking"."Booking_questionnaire" bq
    USING "Booking"."Booking" b
    WHERE b.id = bq."Booking_id"
    AND "Questionnaire_type" = 'checkin'
    AND bq."Completed" IS NULL
    AND COALESCE(b."Check_in", b."Date_from") < (CURRENT_DATE - INTERVAL '7 days');
  EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error borrando cuestionarios checkin: % %', SQLSTATE, SQLERRM;
  END; 

END;
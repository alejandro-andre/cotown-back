-- Actualizacion planificada de status
BEGIN

  RESET ROLE;

  -- Caduca las solicitudes pendientes de pago pasadas de fecha
  UPDATE "Booking"."Booking" 
  SET "Status"='caducada' 
  WHERE "Booking"."Expiry_date" < CURRENT_DATE 
  AND "Booking"."Status"='pendientepago';

  -- Actualiza el estado a 'descartada' de todas las solicitudes que esten caducadas con la fecha de caducidad a NULL o
  -- con la fecha de caducidad 5 dias menor que la fecha en curso.
  UPDATE "Booking"."Booking" 
  SET "Status"='descartada' 
  WHERE "Booking"."Status"='caducada' 
  AND ("Booking"."Expiry_date" IS NULL OR "Booking"."Expiry_date" < (CURRENT_DATE + INTERVAL '5 days'));

  -- Actualiza el estado a 'descartada' de todas las solicitudes que no hayan pagado el deposito y falte menos de un 
  -- mes para la fecha de entrada, con periodo de gracia de 48h desde la creación del pago
  UPDATE "Booking"."Booking" b
  SET "Status" = 'descartadapagada'
  WHERE b."Status" = 'confirmada'
  AND b."Date_from" < (CURRENT_DATE + INTERVAL '30 days')
  AND EXISTS (
    SELECT id 
    FROM "Billing"."Payment" p
    WHERE p."Booking_id" = b.id
    AND p."Payment_type" = 'deposito'
  	AND p."Issued_date" < (CURRENT_DATE - INTERVAL '2 days')
  );

  -- Actualiza el estado a 'check_in' de todas las reservas que tienen que entrar en el dia en curso
  UPDATE "Booking"."Booking" 
  SET "Status"='checkin' 
  WHERE CURRENT_DATE >= GREATEST("Booking"."Check_in", "Booking"."Date_from")
  AND ("Booking"."Status"='checkinconfirmado' OR "Booking"."Status"='contrato');

  -- Actualiza el estado a 'check_out' de todas las reservas que tienen que salir en el dia en curso
  UPDATE "Booking"."Booking" 
  SET "Status"='checkout' 
  WHERE CURRENT_DATE >= GREATEST("Booking"."Check_out", "Booking"."Date_to")
  AND "Booking"."Status"='inhouse';

END;
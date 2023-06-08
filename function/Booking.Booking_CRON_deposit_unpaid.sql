-- Actualiza el estado a 'descartada' de todas las solicitudes que no hayan pagado el deposito y falte menos de un 
-- mes para la fecha de entrada, con periodo de gracia de 48h desde la creación del pago
BEGIN
  RESET ROLE;
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
END;
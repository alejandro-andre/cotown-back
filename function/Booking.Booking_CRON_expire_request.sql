-- Caduca las solicitudes pendientes de pago pasadas de fecha
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" 
  SET "Status"='caducada' 
  WHERE "Booking"."Expiry_date" < CURRENT_DATE 
  AND "Booking"."Status"='pendientepago';
END;
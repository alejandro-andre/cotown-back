-- Actualiza el estado a 'check_in' de todas las reservas que tienen que entrar en el dia en curso
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" 
  SET "Status"='checkin' 
  WHERE CURRENT_DATE >= GREATEST("Booking"."Check_in", "Booking"."Date_from")
  AND ("Booking"."Status"='checkinconfirmado' OR "Booking"."Status"='contrato');
END;
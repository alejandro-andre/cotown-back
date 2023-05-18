-- Actualiza el estado a 'check_out' de todas las reservas que tienen que salir en el dia en curso
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" 
  SET "Status"='checkout' 
  WHERE CURRENT_DATE >= GREATEST("Booking"."Check_out", "Booking"."Date_to")
  AND "Booking"."Status"='inhouse';
END;
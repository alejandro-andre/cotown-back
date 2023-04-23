-- Actualiza el estado a 'check_out' de todas las reservas que tienen que salir en el dia en curso
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" SET "Status"='checkout' WHERE "Booking"."Check_out" = CURRENT_DATE AND "Booking"."Status"='checkin';
END;
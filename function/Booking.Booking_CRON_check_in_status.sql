-- Actualiza el estado a 'check_in' de todas las reservas que tienen que entrar en el dia en curso
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" SET "Status"='checkin' WHERE "Booking"."Check_in" <= CURRENT_DATE AND "Booking"."Status"='checkinconfirmado';
END;
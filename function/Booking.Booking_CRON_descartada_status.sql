-- Actualiza el estado a 'descartada' de todas las solicitudes que esten caducadas con la fecha de caducidad a NULL o
-- con la fecha de caducidad 5 dias menor que la fecha en curso.
BEGIN
  RESET ROLE;
  UPDATE "Booking"."Booking" SET "Status"='descartada' 
  WHERE "Booking"."Status"='caducada' AND ("Booking"."Expiry_date" IS NULL OR "Booking"."Expiry_date" < (CURRENT_DATE + INTERVAL '5 days'));
END;
-- Actualiza la fecha de fin de contrato para edad avanzada (1 año)
BEGIN
  
  UPDATE "Booking"."Booking_other" b
  SET "Date_estimated" = date_trunc('month', current_date + interval '1 year')::date
  WHERE b."Substatus_id" = 2;

END;
-- Actualiza la fecha de fin de contrato para edad avanzada (2 años)
BEGIN
  
  -- Actualiza el estado de las reservas de mayores de 90 años
  UPDATE "Booking"."Booking_other" b
  SET "Substatus_id" = 2
  FROM "Customer"."Customer" c
  WHERE c.id = b."Customer_id"
    AND c."Birth_date" < (CURRENT_DATE - INTERVAL '90 years')
    AND b."Date_estimated" > CURRENT_DATE
    AND b."Substatus_id" <> 2;

  -- Actualiza fin de contrato
  UPDATE "Booking"."Booking_other" b
  SET "Date_estimated" = (date_trunc('month', current_date + interval '2 year') + interval '1 month' - interval '1 day')::date,
      "Date_precapex" = NULL,
      "Date_capex" = NULL
  WHERE b."Substatus_id" = 2;

END;
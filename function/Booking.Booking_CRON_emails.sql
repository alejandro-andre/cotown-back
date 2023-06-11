-- Envio planificado de emails
DECLARE

  booking_id INTEGER;
  customer_id INTEGER;
  num INTEGER;
  
  -- Faltan menos de 40 dias, y no se ha enviado recordatorio
  deposit CURSOR FOR 
    SELECT b.id, b."Customer_id", ce.id
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce 
      ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" = 'deposito'
    WHERE b."Status" = 'confirmada'
    AND ce.id IS NULL
    AND b."Date_from" < (CURRENT_DATE + INTERVAL '40 days');

  -- Faltan menos de 30 dias, y no se ha enviado recordatorio
  depositrecall CURSOR FOR 
    SELECT b.id, b."Customer_id", ce.id
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce 
      ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" = 'depositorecall'
    WHERE b."Status" = 'confirmada'
    AND ce.id IS NULL
    AND b."Date_from" < (CURRENT_DATE + INTERVAL '32 days');

BEGIN

  RESET ROLE;

  -- Envia email diciendo que ya se puede pagar el deposito
  OPEN deposit;
  FETCH deposit INTO booking_id, customer_id;
  WHILE (FOUND) LOOP
    INSERT INTO "Customer"."Customer_email" 
           ("Customer_id", "Template", "Entity_id") 
           VALUES (customer_id, 'deposito', booking_id);
    FETCH deposit INTO booking_id, customer_id;
  END LOOP;
  CLOSE deposit;

  -- Envia email recordando el pago del deposito
  OPEN depositrecall;
  FETCH depositrecall INTO booking_id, customer_id;
  WHILE (FOUND) LOOP
    INSERT INTO "Customer"."Customer_email" 
           ("Customer_id", "Template", "Entity_id") 
           VALUES (customer_id, 'depositorecall', booking_id);
    FETCH depositrecall INTO booking_id, customer_id;
  END LOOP;
  CLOSE depositrecall;

END;
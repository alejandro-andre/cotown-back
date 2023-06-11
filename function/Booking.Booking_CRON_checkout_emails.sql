-- Envio planificado de emails
DECLARE

  booking_id INTEGER;
  customer_id INTEGER;
  
  -- Faltan menos de 10 dias para el checkout
  curs CURSOR FOR 
    SELECT b.id, b."Customer_id", ce.id
     FROM "Booking"."Booking" b
     LEFT JOIN "Customer"."Customer_email" ce 
       ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" = 'checkoutproximo'
    WHERE b."Status" = 'inhouse'
    AND ce.id IS NULL
    AND LEAST(b."Date_to", b."Check_out") < (CURRENT_DATE + INTERVAL '10 days');

BEGIN

  RESET ROLE;

  -- Envia email
  OPEN curs;
  FETCH curs INTO booking_id, customer_id;
  WHILE (FOUND) LOOP
    INSERT INTO "Customer"."Customer_email" 
           ("Customer_id", "Template", "Entity_id") 
           VALUES (customer_id, 'checkoutproximo', booking_id);
    FETCH curs INTO booking_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

-- Envio planificado de emails
DECLARE

  booking_id INTEGER;
  customer_id INTEGER;
  
  -- Pago no realizado hace más de 3 días y no recordado hace menos de 3 días
  curs CURSOR FOR 
    SELECT b.id, b."Customer_id"
     FROM "Billing"."Payment" b
     LEFT JOIN "Customer"."Customer_email" ce 
       ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" = 'pago'
    WHERE b."Payment_date" IS NULL 
      -- Pago retrasado 3 dias
      AND b."Issued_date" < (CURRENT_DATE - INTERVAL '3 days')                    
      -- Recodatorio hace más de 3 dias
      AND (ce.id IS NULL OR ce."Created_at" < (CURRENT_DATE - INTERVAL '3 days'));

BEGIN

  RESET ROLE;

  -- Envia email recordando el pago
  OPEN curs;
  FETCH curs INTO booking_id, customer_id;
  WHILE (FOUND) LOOP
    INSERT INTO "Customer"."Customer_email" 
           ("Customer_id", "Template", "Entity_id") 
           VALUES (customer_id, 'pagorecall', booking_id);
    FETCH curs INTO booking_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

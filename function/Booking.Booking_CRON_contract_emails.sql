-- Envio planificado de emails
DECLARE

  booking_id INTEGER;
  customer_id INTEGER;
  
  -- Contrato no firmado
  curs CURSOR FOR 
    SELECT b.id, b."Customer_id"
     FROM "Booking"."Booking" b
     LEFT JOIN "Customer"."Customer_email" ce 
       ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" LIKE 'firmacontrato%'
    WHERE b."Contract_rent" IS NOT NULL 
      AND b."Contract_signed" IS NULL 
      -- Recodatorio hace más de 3 dias
      AND (ce.id IS NULL OR ce."Created_at" < (CURRENT_DATE - INTERVAL '3 days'));

BEGIN

  RESET ROLE;

  -- Envia email recordando la firma
  OPEN curs;
  FETCH curs INTO booking_id, customer_id;
  WHILE (FOUND) LOOP
    INSERT INTO "Customer"."Customer_email" 
           ("Customer_id", "Template", "Entity_id") 
           VALUES (customer_id, 'firmacontratorecall', booking_id);
    FETCH curs INTO booking_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

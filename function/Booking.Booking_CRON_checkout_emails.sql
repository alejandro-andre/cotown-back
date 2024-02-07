-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Faltan menos de 10 dias para el checkout y no se ha enviado recordatorio
  curs CURSOR FOR
    SELECT b.id, b."Customer_id", ce.id
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce
      ON ce."Customer_id" = b."Customer_id"
      AND ce."Entity_id" = b.id
      AND ce."Template" = 'checkoutproximo'
    WHERE b."Status" = 'inhouse'
    AND LEAST(b."Date_to", b."Check_out") <= (CURRENT_DATE + INTERVAL '10 days')
    AND ce.id IS NULL;

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Envia email recordando checkout
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'checkoutproximo', entity_id);

    -- Questionnaire
    INSERT INTO "Booking"."Booking_questionnaire" ("Booking_id", "Questionnaire_type") VALUES (entity_id, 'checkout');

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

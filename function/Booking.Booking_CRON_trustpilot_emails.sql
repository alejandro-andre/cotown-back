-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Faltan menos de 30 dias para el checkout y no se ha enviado email
  curs CURSOR FOR
    SELECT b.id, b."Customer_id", ce.id
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce
      ON ce."Customer_id" = b."Customer_id"
      AND ce."Entity_id" = b.id
      AND ce."Template" = 'trustpilot'
    WHERE b."Status" = 'inhouse'
    AND COALESCE(b."Check_out", b."Date_to") <= (CURRENT_DATE + INTERVAL '30 days')
    AND ce.id IS NULL
    AND b."Destination_id" IS NULL;

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP
    -- Envía email
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'trustpilot', entity_id);
    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;
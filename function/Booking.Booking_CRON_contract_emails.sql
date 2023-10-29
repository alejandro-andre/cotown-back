-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Contrato no firmado, email de aviso hace mas de tres días
  curs CURSOR FOR
    SELECT b.id, b."Customer_id"
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce
      ON ce."Customer_id" = b."Customer_id"
      AND ce."Entity_id" = b.id
      AND ce."Template" LIKE 'firmacontrato'
    WHERE b."Status" = 'firmacontrato'
    AND b."Contract_signed" IS NULL
    AND ce."Created_at" < (CURRENT_DATE - INTERVAL '3 days');

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un recordatorio de hace menos de 3 dias, envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = "firmacontratorecall"
  		AND "Customer_id" = customer_id
  		AND "Entity_id" = entity_id
  		AND "Created_at" > (CURRENT_DATE - INTERVAL '3 days')
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'firmacontratorecall', entity_id);
   	END IF;

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

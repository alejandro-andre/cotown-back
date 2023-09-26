-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
  
  -- Confirmadas, faltan menos de 40 dias para entrar, y no se ha enviado recordatorio
  curs CURSOR FOR 
    SELECT b.id, b."Customer_id", ce.id
    FROM "Booking"."Booking" b
    LEFT JOIN "Customer"."Customer_email" ce 
      ON ce."Customer_id" = b."Customer_id" 
      AND ce."Entity_id" = b.id 
      AND ce."Template" = 'deposito'
    WHERE b."Status" = 'confirmada'
    AND GREATEST(b."Date_from", b."Check_in") <= (CURRENT_DATE + INTERVAL '40 days')
    AND ce.id IS NULL;

  -- Confirmadas, faltan menos de 32 dias para entrar
  cursrecall CURSOR FOR 
    SELECT b.id, b."Customer_id"
    FROM "Booking"."Booking" b
    WHERE b."Status" = 'confirmada'
    AND GREATEST(b."Date_from", b."Check_in") <= (CURRENT_DATE + INTERVAL '32 days');

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Envia email diciendo que ya se puede pagar el deposito
    INSERT INTO "Customer"."Customer_email"  ("Customer_id", "Template", "Entity_id")  VALUES (customer_id, 'deposito', entity_id);

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

  OPEN cursrecall;
  FETCH cursrecall INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si se ha enviado el primer mail hace mas de 2 dias, envia email recordando el pago del deposito, 
  	IF NOT EXISTS (
  		SELECT id 
  		FROM "Customer"."Customer_email" 
  		WHERE "Customer_id" = customer_id 
  		AND "Entity_id" = entity_id 
  		AND "Template" LIKE 'deposito%'
  		AND "Created_at" > (CURRENT_DATE - INTERVAL '2 days')
  	) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")  VALUES (customer_id, 'depositorecall', entity_id);
   	END IF;

    FETCH cursrecall INTO entity_id, customer_id;
  END LOOP;
  CLOSE cursrecall;

END;
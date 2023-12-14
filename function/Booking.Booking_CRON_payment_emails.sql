-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Pago no realizado hace más de 8 días (1 al 5 + 3)
  -- ERROR: PIDE EL PAGO DE DEPOSITO EMITIDO AUNQUE HAYA PLAZO PARA PAGRLO
  curs CURSOR FOR
    SELECT b.id, b."Customer_id"
    FROM "Billing"."Payment" b
    WHERE b."Payment_type" = 'servicios'
    AND b."Payment_date" IS NULL
    AND b."Issued_date" <= (CURRENT_DATE - INTERVAL '8 days');                   

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un recordatorio de hace menos de 3 dias, envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = 'pagorecall'
  		AND "Customer_id" = customer_id
  		AND "Entity_id" = entity_id
  		AND "Created_at" > (CURRENT_DATE - INTERVAL '3 days')
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'pagorecall', entity_id);
   	END IF;

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Pago no realizado hace más de 8 días (5 días + 3)
  c_first CURSOR FOR
    SELECT b.id, b."Customer_id"
    FROM "Billing"."Payment" b
    WHERE b."Payment_type" = 'servicios'
    AND b."Payment_date" IS NULL
    AND b."Payment_method_id" = 1
    AND b."Issued_date" <= (CURRENT_DATE - INTERVAL '8 days');

  -- Pago no realizado hace más de 13 días (10 días + 3)
  c_next CURSOR FOR
    SELECT b.id, b."Customer_id"
    FROM "Billing"."Payment" b
    WHERE b."Payment_type" = 'servicios'
    AND b."Payment_date" IS NULL
    AND b."Payment_method_id" = 1
    AND b."Issued_date" <= (CURRENT_DATE - INTERVAL '13 days');

BEGIN

  RESET ROLE;

  -- Primer aviso
  OPEN c_first;
  FETCH c_first INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un recordatorio envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = 'pagorecall'
  		AND "Customer_id" = customer_id
  		AND "Entity_id" = entity_id
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'pagorecall', entity_id);
   	END IF;

    FETCH c_first INTO entity_id, customer_id;
  END LOOP;
  CLOSE c_first;

  -- Segundd aviso
  OPEN c_next;
  FETCH c_next INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un recordatorio hace menos de tres dias envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = 'pagorecallagain'
  		AND "Customer_id" = customer_id
  		AND "Entity_id" = entity_id
  		AND "Created_at" > (CURRENT_DATE - INTERVAL '3 days')
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'pagorecallagain', entity_id);
   	END IF;

    FETCH c_next INTO entity_id, customer_id;
  END LOOP;
  CLOSE c_next;
  
END;

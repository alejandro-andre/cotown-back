-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Faltan menos de 30 dias para el checkin
  curs CURSOR FOR
    SELECT b.id, b."Customer_id"
    FROM "Booking"."Booking" b
    WHERE b."Status" IN ('firmacontrato', 'contrato', 'checkinconfirmado')
    AND COALESCE(b."Check_in", b."Date_from") <= (CURRENT_DATE + INTERVAL '30 days')
    AND b."Origin_id" IS NULL;

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un mensaje, envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = 'completachekin'
  		AND "Customer_id" = customer_id
  		AND "Entity_id" = entity_id
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'completacheckin', entity_id);
    ELSE
      -- Si no hay un recordatorio de hace menos de 5 dias, envia uno
      IF NOT EXISTS (
   		  SELECT id
  		  FROM "Customer"."Customer_email"
  		  WHERE "Template" LIKE "completachekin%"
  		  AND "Customer_id" = customer_id
  		  AND "Entity_id" = entity_id
  		  AND "Created_at" > (CURRENT_DATE - INTERVAL '5 days')
      ) THEN
        INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'completacheckinrecall', entity_id);
   	  END IF;
    END IF;

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

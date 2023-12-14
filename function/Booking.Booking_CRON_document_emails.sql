-- Envio planificado de emails
DECLARE

  entity_id INTEGER;
  customer_id INTEGER;
 
  -- Falta documentación, menos de 20 dias para entrar y una reserva viva
  curs CURSOR FOR
    SELECT cd.id, cd."Customer_id"
    FROM "Customer"."Customer_doc" cd
    INNER JOIN "Customer"."Customer_doc_type" cdt ON cdt.id = cd."Customer_doc_type_id" 
    LEFT JOIN "Booking"."Booking" b ON cd."Customer_id" = b."Customer_id"
    WHERE b."Status" IN ('firmacontrato', 'checkinconfirmado', 'checkin', 'inhouse')
  	AND GREATEST(b."Date_from", b."Check_in") <= (CURRENT_DATE + INTERVAL '20 days')
    AND cdt."Mandatory" 
  	AND cd."Document" IS NULL;

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO entity_id, customer_id;
  WHILE (FOUND) LOOP

    -- Si no hay un recordatorio de hace menos de 7 dias, envia uno
    IF NOT EXISTS (
		  SELECT id
  		FROM "Customer"."Customer_email"
  		WHERE "Template" = 'documentacion'
  		AND "Customer_id" = customer_id
  		AND "Created_at" > (CURRENT_DATE - INTERVAL '7 days')
    ) THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'documentacion', entity_id);
   	END IF;

    -- Envía recordatorio

    FETCH curs INTO entity_id, customer_id;
  END LOOP;
  CLOSE curs;

END;

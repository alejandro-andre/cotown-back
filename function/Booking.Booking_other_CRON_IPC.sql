-- Update IPC
DECLARE

  ipc_value NUMERIC;
  rec RECORD;

  -- IPC en dos meses
  ipc_notify CURSOR FOR
  SELECT *
  FROM "Booking"."Booking_other"
  WHERE ("Date_to" > CURRENT_DATE OR "Date_to" IS NULL)
    AND EXTRACT(MONTH FROM CURRENT_DATE + INTERVAL '2 month') = "IPC_month"
    AND ("IPC_notified" IS NULL OR EXTRACT(YEAR FROM "IPC_notified") < EXTRACT(YEAR FROM CURRENT_DATE + INTERVAL '2 month'));

  -- IPC proximo mes
  ipc_update CURSOR FOR
  SELECT *
  FROM "Booking"."Booking_other"
  WHERE ("Date_to" > CURRENT_DATE OR "Date_to" IS NULL)
    AND EXTRACT(MONTH FROM CURRENT_DATE + INTERVAL '1 month') = "IPC_month"
    AND ("IPC_updated" IS NULL OR EXTRACT(YEAR FROM "IPC_updated") < EXTRACT(YEAR FROM CURRENT_DATE + INTERVAL '1 month'));

BEGIN

  -- Obtener el último valor del IPC
  BEGIN
    SELECT "Value_IPC" INTO ipc_value FROM "Auxiliar"."Ipc" ORDER BY "Date_IPC" DESC LIMIT 1;
  EXCEPTION WHEN NO_DATA_FOUND THEN
    RAISE EXCEPTION 'No hay valores de IPC en Auxiliar.Ipc';
  END;

  -- Abrir cursor y recorrer fila a fila
  OPEN ipc_notify;
  FETCH ipc_notify INTO rec;
  WHILE FOUND LOOP

    -- Actualizar fila
    UPDATE "Booking"."Booking_other"
    SET
      "Applied_IPC" = ipc_value,
      "IPC_notified" = CURRENT_DATE
    WHERE id = rec.id;

    -- Mostrar valores
    RAISE NOTICE 'Booking: %, IPC aplicado: %', rec.id, ipc_value;

    -- Enviar correo
    IF rec."Send_IPC" THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (rec."Customer_id", 'ipc', rec.id);
    END IF;

    -- Siguiente
    FETCH ipc_notify INTO rec;
  END LOOP;
  CLOSE ipc_notify;

  -- Abrir cursor y recorrer fila a fila
  OPEN ipc_update;
  FETCH ipc_update INTO rec;
  WHILE FOUND LOOP

    -- Actualizar fila
    UPDATE "Booking"."Booking_other"
    SET
      "Prev_rent" = rec."Rent",
      "Rent" = ROUND(rec."Rent" * (1 + COALESCE(rec."Applied_IPC", 0) / 100), 2),
      "IPC_updated" = CURRENT_DATE
    WHERE id = rec.id;

    -- Mostrar valores
    RAISE NOTICE 
      'Booking: %, Renta anterior: %, IPC aplicado: %, Renta nueva: %', 
      rec.id, 
      rec."Rent", 
      COALESCE(rec."Applied_IPC", 0), 
      ROUND(rec."Rent" * (1 + COALESCE(rec."Applied_IPC", 0) / 100), 2);

    -- Siguiente
    FETCH ipc_update INTO rec;
  END LOOP;
  CLOSE ipc_update;

END;
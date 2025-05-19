-- Update IPC
DECLARE

  ipc_value NUMERIC;
  rec RECORD;

  -- IPC en dos meses
  cur CURSOR FOR
  SELECT *
    FROM "Booking"."Booking_other"
    WHERE ("Date_to" > CURRENT_DATE OR "Date_to" IS NULL)
      AND EXTRACT(MONTH FROM CURRENT_DATE + INTERVAL '1 month') = "IPC_month"
      AND EXTRACT(YEAR FROM "IPC_updated") < EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month');

BEGIN

  -- Obtener el último valor del IPC
  SELECT "Value_IPC" INTO ipc_value FROM "Auxiliar"."Ipc" ORDER BY "Date_IPC" DESC LIMIT 1;

  -- Abrir cursor y recorrer fila a fila
  OPEN cur;
  FETCH cur INTO rec;
  WHILE (FOUND) LOOP

    -- Actualizar fila
    UPDATE "Booking"."Booking_other"
    SET
      "Prev_rent" = rec."Rent",
      "Rent" = ROUND(rec."Rent" * (1 + ipc_value / 100) * 100) / 100,
      "Applied_IPC" = ipc_value,
      "IPC_updated" = CURRENT_DATE
    WHERE id = rec.id;

    -- Mostrar valores
    RAISE NOTICE 'ID: %, Renta anterior: %, IPC aplicado: %, Renta nueva: %', rec."Id", rec."Rent", ipc_value, ROUND(rec."Rent" * (1 + ipc_value / 100) * 100) / 100;

    -- Enviar correo
    IF rec."Send_IPC" THEN
      INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (rec."Customer_id", 'ipc', rec.id);
    END IF;

    -- Siguiente
    FETCH cur INTO rec;
  END LOOP;
  CLOSE cur;

END;
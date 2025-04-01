-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;
  customer_id INTEGER;
  id_type_id INTEGER;
  reason_id INTEGER;
  reg RECORD;
  num INTEGER;
  curr_user VARCHAR;
  billing_type VARCHAR;
  black_list BOOLEAN;
  black_reason VARCHAR;
  
BEGIN

  -- Superuser ROLE 
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Tipología obligatoria
  IF NEW."Resource_type" <> 'piso' AND NEW."Place_type_id" IS NULL THEN
    RAISE exception '!!!Place type is mandatory!!!El tipo de plaza es obligatoria!!!'; 	
  END IF;

  -- Comprueba si existen las tipologías seleccionadas en el edificio
  SELECT COUNT(*)
  INTO num
  FROM "Resource"."Resource" r
  WHERE "Building_id" = NEW."Building_id"
  AND r."Flat_type_id" = NEW."Flat_type_id"
  AND r."Place_type_id" = NEW."Place_type_id";

  -- Reserva bloqueada?
  IF NEW."Lock" AND
    OLD."Resource_id" IS NOT NULL AND
    OLD."Resource_id" <> NEW."Resource_id" THEN
    RAISE exception '!!!Locked booking!!!Reserva bloqueada!!!';
  END IF;

  -- Verifica las fechas
  IF NEW."Check_in" < '2000-01-01' THEN
    NEW."Check_in" = NULL;
  END IF;
  IF NEW."Check_out" < '2000-01-01' THEN
    NEW."Check_out" = NULL;
  END IF;
  IF NEW."Expiry_date" < '2000-01-01' THEN
    NEW."Expiry_date" = NULL;
  END IF;
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;

  -- Valida que las fechas de checkin estén en el rango correcto
  IF NEW."Check_in" IS NOT NULL THEN
    IF NEW."Check_in" < NEW."Date_from"THEN
      RAISE exception '!!!Check-in date cannot be earlier than the start of the reservation!!!Fecha de check in no puede ser anterior al inicio de la reserva!!!';
    END IF;
    IF NEW."Check_in" >= NEW."Date_to"THEN
      RAISE exception '!!!Check-in date cannot be later than the end of the reservation!!!Fecha de check in no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Valida que las fechas de checkout estén en el rango correcto
  IF NEW."Check_out" IS NOT NULL THEN
    IF NEW."Check_out" < NEW."Check_in"THEN
      RAISE exception '!!!Check-out date cannot be earlier than the check-in date!!!Fecha de check out no puede ser anterior al check-in!!!';
    END IF;
    IF NEW."Check_out" > NEW."Date_to"THEN
      RAISE exception '!!!Check-out date cannot be later than the end of the reservation!!!Fecha de check out no puede ser posterior al final de la reserva!!!';
    END IF;
  END IF;

  -- Valida que la nueva fecha de checkout es valida
  IF NEW."New_check_out" IS NOT NULL THEN
    IF NEW."New_check_out" < COALESCE(NEW."Check_in", NEW."Date_from") THEN
      RAISE exception '!!!New check-out is wrong!!!Nueva fecha de check out incorrecta!!!';
    END IF;
  END IF;

  -- Valida que las fechas de solicitud sea menor que la fecha de expiracion
  IF NEW."Expiry_date" IS NOT NULL THEN
    IF NEW."Expiry_date" < NEW."Request_date"· THEN
      RAISE EXCEPTION '!!!The expiry date must be equal to or greater than the date of application.!!!La fecha de expiración debe ser igual o mayor a la fecha de solicitud!!!';
    END IF;
  END IF;

  -- Fecha de solicitud
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Deposit
  IF COALESCE(NEW."Deposit_returned", 0) > COALESCE(NEW."Deposit_actual", 0) THEN
    RAISE EXCEPTION '!!!Returned deposit greater than actual.!!!Garantía devuelta superior a la depositada!!!';
  END IF;

  -- Check for overlaps
  IF NEW."Status" NOT IN ('descartada', 'descartadapagada', 'cancelada', 'caducada', 'finalizada') THEN
    SELECT b."Booking_id"
    INTO num
    FROM "Booking"."Booking_detail" b 
    WHERE b."Resource_id" = NEW."Resource_id"
    AND b."Booking_id" <> NEW.id
    AND b."Date_from" <= NEW."Date_to" 
    AND b."Date_to" >= NEW."Date_from"
    LIMIT 1;
    IF num IS NOT NULL THEN
      RAISE exception '!!!Overlaping % with booking %!!!Solapamiento % con la reserva %!!!', NEW.id, num, NEW.id, num;
    END IF;
  END IF;

  -- Valida cliente no en lista negra
  SELECT c."Id_type_id", c."Black_list", c."Black_reason" INTO id_type_id, black_list, black_reason FROM "Customer"."Customer" c WHERE c.id = NEW."Customer_id";
  IF black_list = TRUE THEN
    IF NEW."Ignore_black_list" = TRUE 
    THEN
    ELSE
      RAISE exception '!!!Customer on black list: "%"!!!Cliente en lista negra: "%"!!!', black_reason, black_reason;
    END IF;
  END IF;

  -- Reason
  IF NEW."Reason_id" IS NULL AND NEW."Status" NOT IN ('descartada', 'descartadapagada', 'cancelada', 'caducada', 'finalizada') THEN
    RAISE exception '!!!Reason not selected!!!Motivo no seleccionado!!!';
  END IF;
  IF NEW."Reason_id" IN (1, 3) THEN
    IF NEW."School_id" IS NULL THEN
      RAISE exception '!!!School not selected!!!Escuela no seleccionada!!!';
    END IF;
    IF NEW."School_id" = 1 AND NEW."Other_school" IS NULL THEN
      RAISE exception '!!!School (other) not completed!!!Escuela (otra) no indicada!!!';
    END IF;
  END IF;
  IF NEW."Reason_id" IN (2, 3, 4) THEN
    IF NEW."Company" IS NULL THEN
      RAISE exception '!!!Company not completed!!!Compañía no indicada!!!';
    END IF;
  END IF;

  -- Documentos obligatorios
  INSERT INTO "Customer"."Customer_doc" ("Customer_id", "Customer_doc_type_id")
    SELECT NEW."Customer_id", id
    FROM "Customer"."Customer_doc_type" cdt
    WHERE "Mandatory" = TRUE
    AND (
      cdt."Reason_id" = NEW."Reason_id" OR
      cdt."Id_type_id" = id_type_id OR
      (cdt."Reason_id" IS NULL AND cdt."Id_type_id" IS NULL)
    )
  ON CONFLICT ("Customer_id", "Customer_doc_type_id") DO NOTHING;
 
  -- Billing type
  IF NEW."Resource_id" IS NOT NULL AND (NEW."Billing_type" IS NULL OR NEW."Billing_type_last" IS NULL ) THEN
    SELECT "Billing_type" INTO billing_type FROM "Resource"."Resource" WHERE id = NEW."Resource_id";
    IF NEW."Billing_type" IS NULL THEN
      NEW."Billing_type" = billing_type;
    END IF;
    IF NEW."Billing_type_last" IS NULL THEN
      NEW."Billing_type_last" = billing_type;
    END IF;
  END IF;

  -- Return record
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
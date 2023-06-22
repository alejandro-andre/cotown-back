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
  --?IF num < 1 THEN
  --?  RAISE exception '!!!Selected flat/place type doesnt exist on that building!!!Las tipologías elegidas no existen en el edificio!!!'; 	
  --?END IF;
 
  -- Reserva bloqueada?
  IF NEW."Lock" AND 
    OLD."Resource_id" IS NOT NULL AND
    OLD."Resource_id" <> NEW."Resource_id" THEN
    RAISE exception '!!!Locked booking!!!Reserva bloqueada!!!';
  END IF;

  -- Se ha intentado quitar el recurso?
  IF OLD."Resource_id" IS NOT NULL AND NEW."Resource_id" IS NULL THEN
    RAISE exception '!!!Resource cannot be removed!!!El recurso no se puede quitar!!!';
  END IF;

  -- Verifica las fechas
  IF NEW."Check_in" < '2000-01-01' THEN
    NEW."Check_in" = NULL;
  END IF;
  IF NEW."Check_out" < '2000-01-01' THEN
    NEW."Check_out" = NULL;
  END IF;
  IF NEW."Contract_signed" < '2000-01-01' THEN
    NEW."Contract_signed" = NULL;
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

  -- Valida que las fechas de solicitud sea menor que la fecha de expiracion
  IF NEW."Expiry_date" IS NOT NULL THEN
    IF NEW."Expiry_date" < NEW."Request_date"· THEN
      RAISE EXCEPTION '!!!The expiry date must be equal to or greater than the date of application.!!!La fecha de expiración debe ser igual o mayor a la fecha de solicitud!!!';
    END IF;
  END IF;

  -- Si no hay pagador, es el cliente
  IF NEW."Payer_id" IS NULL THEN
    NEW."Payer_id" = NEW."Customer_id";
  END IF;

  -- Fecha de solicitud
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Get customer id type
  SELECT c."Id_type_id" INTO id_type_id FROM "Customer"."Customer" c WHERE c.id = NEW."Customer_id";
 
  -- Documentos obligatorios
  DELETE FROM "Customer"."Customer_doc" WHERE "Document" IS NULL;
  INSERT INTO "Customer"."Customer_doc" ("Customer_id", "Customer_doc_type_id") 
    SELECT NEW."Customer_id", id
    FROM "Customer"."Customer_doc_type" cdt
    WHERE "Mandatory" = TRUE
    AND (cdt."Reason_id" = NEW."Reason_id" OR cdt."Id_type_id" = id_type_id)
  ON CONFLICT ("Customer_id", "Customer_doc_type_id") DO NOTHING;
  
  -- Return record
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
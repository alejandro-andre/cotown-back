-- Verifica los datos de la reserva
DECLARE

  days INTEGER;
  months INTEGER;
  years INTEGER;
  duration INTERVAL;
  num INTEGER;
  billing_type VARCHAR;

  c_rent INTEGER;
  c_limit INTEGER;
  limit_type VARCHAR;
  
  deposit NUMERIC;
  legal_deposit NUMERIC;

BEGIN

  -- Check request dates
  IF NEW."Date_from" > NEW."Date_to" THEN
    RAISE exception '!!!Wrong dates!!!Fechas incorrectas!!!';
  END IF;
  IF NEW."Date_from" > (SELECT MIN("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents before initial date!!!Hay rentas anteriores a la fecha de inicio!!!';
  END IF;
  IF NEW."Date_from" > (SELECT MIN("Check_in") FROM "Booking"."Booking_group_rooming" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Check-ins before initial date!!!Hay check-ins anteriores a la fecha de inicio!!!';
  END IF;
  IF NEW."Date_to" < (SELECT MAX("Rent_date") FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Rents after finish date!!!Hay rentas posteriores a la fecha de fin!!!';
  END IF;
  IF NEW."Date_to" < (SELECT MAX("Check_out") FROM "Booking"."Booking_group_rooming" bp WHERE bp."Booking_id" = NEW.id) THEN
    RAISE exception '!!!Check-outs after finish date!!!Hay check-outs posteriores a la fecha de fin!!!';
  END IF;

  -- Check the places
  IF (NEW."Rooms" IS NULL OR NEW."Rooms" < 1) THEN
    RAISE exception '!!!Enter the number of places!!!Introduzca el número de plazas!!!';
  END IF;

  -- Cannot cancel booking with invoices
  IF NEW."Status" = 'cancelada' THEN
  	SELECT COUNT(*)
  	INTO num
  	FROM "Billing"."Invoice" i
  	WHERE i."Booking_group_id" = NEW.id;
    IF num > 0 THEN
      RAISE exception '!!!Cannot cancel booking with invoices!!!No se puede cancelar una reserva con facturas!!!';
    END IF;
  END IF;

  -- Request date
  IF NEW."Request_date" IS NULL THEN
    NEW."Request_date" := NOW();
  END IF;

  -- Billing type
  IF NEW."Building_id" IS NOT NULL AND (NEW."Billing_type" IS NULL OR NEW."Billing_type_last" IS NULL ) THEN
    SELECT "Billing_type" INTO billing_type 
    FROM "Resource"."Resource" 
    WHERE "Building_id" = NEW."Building_id" AND "Billing_type" <> 'na' 
    ORDER BY id LIMIT 1;
    IF NEW."Billing_type" IS NULL THEN
      NEW."Billing_type" = billing_type;
    END IF;
    IF NEW."Billing_type_last" IS NULL THEN
      NEW."Billing_type_last" = billing_type;
    END IF;
  END IF;

  -- Rooms changed?
  --IF OLD."Room_ids" = NEW."Room_ids" THEN
  --  RETURN NEW;
  --END IF;

  -- Not tentative?
  IF NEW."Status" <> 'grupobloqueado' THEN
    RETURN NEW;
  END IF;

  -- Check flats limitations and max rent
  SELECT
    COUNT(DISTINCT f."Limit_type"),
    MAX(f."Limit_type"),
    COUNT(DISTINCT CASE
      WHEN (f."Limit_type" IS NULL OR f."Limit_type" = 'libre')
      THEN f."Max_rent"
    END)
  INTO c_limit, limit_type, c_rent
  FROM "Resource"."Resource" f
  WHERE f.id::text = ANY (
    SELECT COALESCE(r."Flat_id"::text, r.id::text)
    FROM "Resource"."Resource" r
    WHERE "Code" = ANY(NEW."Room_ids")
  );
  IF c_limit > 1 THEN
    RAISE EXCEPTION '!!!Flats with different limitation types!!!Pisos con diferentes tipos de limitación!!!';
  END IF;
  IF c_rent > 1 THEN
    RAISE EXCEPTION '!!!Flats with different max rents!!!Pisos con diferentes rentas máximas!!!';
  END IF;
  IF limit_type IN ('lau', 'indice') AND NEW."Book_type" IS NULL THEN
    RAISE EXCEPTION '!!!Wrong book type: resource(s) has limitations!!!Tipo de reserva erróneo: recurso(s) con limitación!!!';
  END IF;

  -- Limited prices
  NEW."Limit_type" = limit_type;
  IF COALESCE(NEW."Rent") = 0 AND limit_type IN ('lau', 'indice') THEN
    SELECT
      AVG(r."Max_rent"),
      AVG(r."Max_services"),
      AVG(r."Max_utility"),
      AVG(r."Max_expenses"),
      AVG(r."Max_furniture")
    INTO NEW."Rent", NEW."Services", NEW."Limit", NEW."Expenses", NEW."Furniture"
    FROM "Resource"."Resource" r
    WHERE r."Code" = ANY(NEW."Room_ids");
  END IF;

  -- Calculate stay length in montns
  SELECT EXTRACT(MONTH FROM AGE(NEW."Date_to", NEW."Date_from")) INTO months;

  -- Deposit
  IF NEW."Full_flat" THEN
    IF NEW."Book_type" = 'limitado' THEN
      legal_deposit := NEW."Rent" + NEW."Limit" + NEW."Furniture" + NEW."Expenses";
      deposit := 1.5 * legal_deposit;
    ELSE
      legal_deposit := months * (NEW."Rent" + NEW."Limit" + NEW."Furniture" + NEW."Expenses") / 6;
      deposit := 1.5 * (NEW."Rent" + NEW."Limit" + NEW."Furniture" + NEW."Expenses");
      IF deposit > legal_deposit THEN
        deposit := deposit - legal_deposit;
      ELSE
        deposit = 0;
      END IF;
    END IF;
  ELSE
    deposit := 1.5 * (NEW."Rent" + NEW."Limit" + NEW."Furniture" + NEW."Expenses");
    legal_deposit := 0;
  END IF;
  NEW."Deposit" = deposit;
  NEW."Incasol_deposit" = legal_deposit;

  -- Return record
  RETURN NEW;

END;
-- Calcula los precios de la reserva
DECLARE

  dt_to DATE;
  dt_curr DATE;
  dt_next DATE;
  dt_intr INTERVAL;

  building_id INTEGER;
  flat_type INTEGER;
  place_type INTEGER;
  billing_type VARCHAR;
  rate INTEGER;
  resource INTEGER;
  multiplier NUMERIC;
  incpct NUMERIC;
  payment_method_id INTEGER;

  months INTEGER;
  days INTEGER;

  cy_rent NUMERIC;
  cy_services NUMERIC;
  cy_limit NUMERIC;
  cy_deposit NUMERIC;
  cy_second NUMERIC;
  cy_final_cleaning NUMERIC;

  ny_rent NUMERIC;
  ny_services NUMERIC;
  ny_limit NUMERIC;
  ny_deposit NUMERIC;
  ny_second NUMERIC;
  ny_final_cleaning NUMERIC;

  m_rent NUMERIC;
  m_services NUMERIC;
  m_limit NUMERIC;
  m_deposit NUMERIC;
  m_final_cleaning NUMERIC;

  num INTEGER;

BEGIN

  -- Update booking fee
  IF OLD."Booking_fee" <> NEW."Booking_fee" THEN

    -- Already payed?
    SELECT COUNT(*) INTO num 
    FROM "Billing"."Payment" 
    WHERE "Customer_id" = NEW."Payer_id" 
      AND "Booking_id" = NEW.id
      AND "Payment_date" IS NOT NULL;
    IF num > 0 THEN
      RAISE EXCEPTION '!!!Booking fee already payed!!!El booking fee ya ha sido pagado!!!';
    END IF;

    -- Update fee (delete + update)
    SELECT "Payment_method_id" INTO payment_method_id FROM "Customer"."Customer" WHERE id = NEW."Payer_id";
    DELETE FROM "Billing"."Payment" WHERE "Customer_id" = NEW."Payer_id" AND "Booking_id" = NEW.id;
    INSERT
      INTO "Billing"."Payment"("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
      VALUES (COALESCE(payment_method_id, 1), NEW."Payer_id", NEW.id, NEW."Booking_fee", CURRENT_DATE, 'Booking fee', 'booking');
  END IF;

  -- No resource
  IF NEW."Resource_id" IS NULL THEN
    RETURN NEW;
  END IF;

  -- Only calc if not yet confirmed
  IF NEW."Status" NOT IN ('solicitud', 'solicitudpagada', 'alternativas', 'alternativaspagada', 'pendientepago') THEN
    RETURN NEW;
  END IF;

  -- Prices already billed? Ignore
  SELECT COUNT(*)
  INTO num
  FROM "Booking"."Booking_price"
  WHERE "Booking_id" = NEW.id
  AND ("Invoice_rent_id" IS NOT NULL OR "Invoice_services_id" IS NOT NULL);
  IF num > 0 THEN
    RETURN NEW;
  END IF;

  -- Prices already calculated and resource or dates not changed? Ignore
  SELECT COUNT(*)
  INTO num
  FROM "Booking"."Booking_price"
  WHERE "Booking_id" = NEW.id;
  IF num > 0 AND NEW."Resource_id" = OLD."Resource_id" AND NEW."Date_from" = OLD."Date_from" AND NEW."Date_to" = OLD."Date_to" THEN
    RETURN NEW;
  END IF;

  -- Delete old prices
  NEW."Rent" := 0;
  NEW."Services" := 0;
  NEW."Deposit" := 0;
  NEW."Limit" := 0;
  NEW."Final_cleaning" := 0;
  DELETE FROM "Booking"."Booking_price"
  WHERE "Booking_id" = NEW.id;

  -- Get resource building, tipology and rate
  SELECT "Building_id", "Flat_type_id", "Place_type_id", "Billing_type", "Rate_id"
  INTO building_id, flat_type, place_type, billing_type, rate
  FROM "Resource"."Resource"
  WHERE id = NEW."Resource_id";

  -- Get amenities
  SELECT COALESCE(SUM("Increment"), 0)
  INTO incpct
  FROM "Resource"."Resource_amenity" ra
  INNER JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id"
  WHERE ra."Resource_id" = NEW."Resource_id"
  AND rat."Increment" > 0;

  -- Get rate multiplier
  SELECT "Multiplier"
  INTO multiplier
  FROM "Billing"."Pricing_rate"
  WHERE id = rate;

  -- Calculate stay length
  dt_curr = NEW."Date_from";
  dt_to = NEW."Date_to" + INTERVAL '1 day';
  SELECT EXTRACT(MONTH FROM AGE(dt_to, dt_curr)) INTO months;

  -- Get current year prices
  SELECT
    CASE
      WHEN months < 3 THEN "Rent_short"
      WHEN months < 7 THEN "Rent_medium"
      ELSE "Rent_long"
    END,
    "Services",
    "Second_resident",
    "Deposit",
    "Limit",
    "Final_cleaning"
  INTO cy_rent, cy_services, cy_second, cy_deposit, cy_limit, cy_final_cleaning
  FROM "Billing"."Pricing_detail"
  WHERE "Building_id" = building_id
  AND "Flat_type_id" = flat_type
  AND ("Place_type_id" = place_type OR ("Place_type_id" IS NULL AND place_type IS NULL))
  AND "Year" = EXTRACT(YEAR FROM dt_curr);
 
  -- Get next year prices
  SELECT
    CASE
      WHEN months < 3 THEN "Rent_short"
      WHEN months < 7 THEN "Rent_medium"
      ELSE "Rent_long"
    END,
    "Services",
    "Second_resident",
    "Deposit",
    "Limit",
    "Final_cleaning"
  INTO ny_rent, ny_services, ny_second, ny_deposit, ny_limit, ny_final_cleaning
  FROM "Billing"."Pricing_detail"
  WHERE "Building_id" = building_id
  AND "Flat_type_id" = flat_type
  AND ("Place_type_id" = place_type OR ("Place_type_id" IS NULL AND place_type IS NULL))
  AND "Year" = 1 + EXTRACT(YEAR FROM dt_curr);

  -- Default prices to 0
  SELECT coalesce(cy_rent, 0), coalesce(cy_services, 0), coalesce(cy_second, 0), coalesce(cy_deposit, 0), coalesce(cy_limit, 0) INTO cy_rent, cy_services, cy_second, cy_deposit, cy_limit;
  SELECT coalesce(ny_rent, 0), coalesce(ny_services, 0), coalesce(ny_second, 0), coalesce(ny_deposit, 0), coalesce(ny_limit, 0) INTO ny_rent, ny_services, ny_second, ny_deposit, ny_limit;
  SELECT coalesce(cy_final_cleaning, 0), coalesce(ny_final_cleaning, 0) INTO cy_final_cleaning, ny_final_cleaning;

  -- Second resident
  IF NEW."Second_resident" THEN
    cy_rent = cy_rent + cy_second;
    ny_rent = ny_rent + ny_second;
  END IF;

  -- Increment factor
  multiplier := multiplier * (1 + (incpct / 100.0));
  cy_rent := cy_rent * multiplier;
  ny_rent := ny_rent * multiplier;

  -- Current year prices
  m_rent := ROUND(cy_rent, 0);
  m_services := ROUND(cy_services, 0);
  m_deposit := ROUND(cy_deposit, 0);
  m_limit := ROUND(cy_limit, 0);
  m_final_cleaning := ROUND(cy_final_cleaning, 0);
  IF EXTRACT(MONTH FROM dt_curr) > 8 OR EXTRACT(YEAR FROM dt_curr) > EXTRACT(YEAR FROM NEW."Date_from") THEN
    m_rent := ROUND(ny_rent, 0);
    m_services := ROUND(ny_services, 0);
    m_deposit := ROUND(ny_deposit, 0);
    m_limit := ROUND(ny_limit, 0);
    m_final_cleaning := ROUND(ny_final_cleaning, 0);
  END IF; 

  -- Insert base values
  IF m_deposit < m_rent + m_services THEN
    m_deposit := m_rent + m_services;
  END IF;
  NEW."Rent" := m_rent;
  NEW."Services" := m_services;
  NEW."Deposit" := m_deposit;
  NEW."Limit" := m_limit;
  NEW."Final_cleaning" := m_final_cleaning;

  -- Insert prices
  WHILE dt_curr < dt_to LOOP

    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);
    dt_intr := AGE(dt_next, dt_curr);
 
    -- Year change?
    IF EXTRACT(MONTH FROM dt_curr) > 8 OR EXTRACT(YEAR FROM dt_curr) > EXTRACT(YEAR FROM NEW."Date_from") THEN
      m_rent := ROUND(ny_rent, 0);
      m_services := ROUND(ny_services, 0);
    END IF; 
 
    -- Incomplete months
    IF dt_intr < INTERVAL '1 month' THEN
     
      IF billing_type = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          m_rent := ROUND(m_rent / 2, 1);
          m_services := ROUND(m_services / 2, 1);
        END IF;
      END IF;
   
      IF billing_type = 'proporcional' THEN
        days := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        m_rent := ROUND(m_rent * EXTRACT(DAY FROM dt_intr) / days, 1);
        m_services := ROUND(m_services * EXTRACT(DAY FROM dt_intr) / days, 1);
      END IF;
   
    END IF;
   
    -- Final cleaning
    IF date_trunc('month', dt_curr) + interval '1 month' >= dt_to AND place_type IS NULL THEN
      m_services := ROUND(m_services + coalesce(m_final_cleaning, 0), 0);
    END IF;
 
    -- Insert price
    INSERT INTO "Booking"."Booking_price"
    ("Booking_id", "Rent_date", "Rent", "Services")
    VALUES (NEW.id, dt_curr, m_rent, m_services);
 
    -- Next month
    dt_curr := date_trunc('month', dt_curr) + interval '1 month';
 
  END LOOP; 

  -- Return
  RETURN NEW;

END;
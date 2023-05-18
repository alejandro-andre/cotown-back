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

  months INTEGER;
  days INTEGER;

  cy_rent NUMERIC;
  cy_services NUMERIC;
  cy_second NUMERIC;
  cy_limit NUMERIC;
  cy_deposit NUMERIC;

  ny_rent NUMERIC;
  ny_services NUMERIC;
  ny_second NUMERIC;
  ny_limit NUMERIC;
  ny_deposit NUMERIC;

  final_cleaning NUMERIC;

  m_rent NUMERIC;
  m_services NUMERIC;
  m_deposit NUMERIC;
  m_limit NUMERIC;

  num INTEGER;

BEGIN

  RESET ROLE;

  -- No resource
  IF NEW."Resource_id" IS NULL THEN
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
  INTO cy_rent, cy_services, cy_second, cy_deposit, cy_limit, final_cleaning
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
    "Limit"
  INTO ny_rent, ny_services, ny_second, ny_deposit, ny_limit
  FROM "Billing"."Pricing_detail"
  WHERE "Building_id" = building_id
  AND "Flat_type_id" = flat_type
  AND ("Place_type_id" = place_type OR ("Place_type_id" IS NULL AND place_type IS NULL))
  AND "Year" = 1 + EXTRACT(YEAR FROM dt_curr);

  -- Default prices to 0
  SELECT coalesce(cy_rent, 0), coalesce(cy_services, 0), coalesce(cy_second, 0), coalesce(cy_deposit, 0), coalesce(cy_limit, 0) INTO cy_rent, cy_services, cy_second, cy_deposit, cy_limit;
  SELECT coalesce(ny_rent, 0), coalesce(ny_services, 0), coalesce(ny_second, 0), coalesce(ny_deposit, 0), coalesce(ny_limit, 0) INTO ny_rent, ny_services, ny_second, ny_deposit, ny_limit;
  SELECT coalesce(final_cleaning, 0) INTO final_cleaning;

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
  m_rent := cy_rent;
  m_services := cy_services;
  m_deposit := cy_deposit;
  m_limit := cy_limit;
  IF EXTRACT(MONTH FROM dt_curr) > 8 OR EXTRACT(YEAR FROM dt_curr) > EXTRACT(YEAR FROM NEW."Date_from") THEN
    m_rent := ny_rent;
    m_services := ny_services;
    m_deposit := ny_deposit;
    m_limit := ny_limit;
  END IF;  

  -- Insert base values
  IF m_deposit < m_rent + m_services THEN
    m_deposit := m_rent + m_services;
  END IF;
  NEW."Rent" := m_rent;
  NEW."Services" := m_services;
  NEW."Deposit" := m_deposit;
  NEW."Limit" := m_limit;

  -- Insert prices
  WHILE dt_curr < dt_to LOOP

    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);
    dt_intr := AGE(dt_next, dt_curr);
  
    -- Year change?
    IF EXTRACT(MONTH FROM dt_curr) > 8 OR EXTRACT(YEAR FROM dt_curr) > EXTRACT(YEAR FROM NEW."Date_from") THEN
      m_rent := ny_rent;
      m_services := ny_services;
    END IF;  
  
    -- Incomplete months
    IF dt_intr < INTERVAL '1 month' THEN
      
      IF billing_type = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          m_rent := m_rent / 2;
          m_services := m_services / 2;
        END IF;
      END IF;
    
      IF billing_type = 'proporcional' THEN
        days := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        m_rent := m_rent * EXTRACT(DAY FROM dt_intr) / days;
        m_services := m_services * EXTRACT(DAY FROM dt_intr) / days;
      END IF;
    
    END IF;
    
    -- Final cleaning
    IF date_trunc('month', dt_curr) + interval '1 month' >= dt_to AND place_type IS NULL THEN
      m_services := m_services + coalesce(final_cleaning, 0);
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
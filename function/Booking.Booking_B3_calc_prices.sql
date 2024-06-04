-- Calcula los precios de la reserva
DECLARE

  curr_user VARCHAR;

  days INTEGER;
  months INTEGER;
  year INTEGER;
 
  dt_to DATE;
  dt_curr DATE;
  dt_next DATE;
  dt_intr INTERVAL;

  billing_type VARCHAR;

  rent NUMERIC;
  services NUMERIC;
  deposit NUMERIC;
  final_cleaning NUMERIC;
  second_resident NUMERIC;
  limit NUMERIC;

  n_rent NUMERIC;
  n_services NUMERIC;

  monthly_rent NUMERIC;
  monthly_services NUMERIC;

  curr_rent NUMERIC;
  curr_services NUMERIC;

  prev_total NUMERIC;
  curr_total NUMERIC;

BEGIN

  -- Date to
  dt_to = NEW."Date_to";

  -- No resource, ignore
  IF NEW."Resource_id" IS NULL THEN
    NEW."Deposit"        := NULL;
    NEW."Rent"           := NULL;
    NEW."Services"       := NULL;
    NEW."Final_cleaning" := NULL;
    NEW."Limit"          := NULL;
    RETURN NEW;
  END IF;

  -- Not ECO_EXT?
  --IF NEW."New_check_out" IS NULL OR NEW."New_check_out" = NEW."Check_out" OR NEW."New_check_out" = NEW."Date_to" THEN
  IF NEW."New_check_out" IS NULL OR NEW."New_check_out" = NEW."Date_to" THEN

    -- Dates and resource not changed, ignore
    IF NEW."Resource_id" = OLD."Resource_id" AND NEW."Date_from" = OLD."Date_from" AND NEW."Date_to" = OLD."Date_to" THEN
      RETURN NEW;
    END IF;

    -- Delete future not billed prices
    DELETE FROM "Booking"."Booking_price"
    WHERE "Booking_id" = NEW.id
      --? AND "Rent_date" > 'CURRENT_DATE'
      AND "Invoice_rent_id" IS NULL
      AND "Invoice_services_id" IS NULL;
 
  -- ECO/EXT
  ELSE

    -- Update dates
    dt_to := NEW."New_check_out";
   
    -- Get previous accumulated rent
    SELECT SUM("Rent") INTO prev_total FROM "Booking"."Booking_price" WHERE "Booking_id" = NEW.id;

    IF NEW."New_check_out" < NEW."Date_to" THEN
      -- ECO: Delete last months price
      DELETE FROM "Booking"."Booking_price"
      WHERE "Booking_id" = NEW.id 
        AND "Invoice_rent_id" IS NULL
        AND "Invoice_services_id" IS NULL
        AND "Rent_date" >= date_trunc('month', LEAST(NEW."New_check_out", NEW."Date_to"));
    ELSE 
      -- EXT: Delete future not billed prices
      DELETE FROM "Booking"."Booking_price"
      WHERE "Booking_id" = NEW.id 
        AND "Rent_date" > CURRENT_DATE
        AND "Invoice_rent_id" IS NULL
        AND "Invoice_services_id" IS NULL;
 	  END IF;
  END IF;

  -- Calculate stay length in montns
  SELECT EXTRACT(MONTH FROM AGE(dt_to, NEW."Date_from")) INTO months;

  -- Calculate year
  SELECT EXTRACT(YEAR FROM NEW."Date_from") INTO year;
  IF EXTRACT(MONTH FROM dt_curr) > 8 THEN
    year := year + 1;
  END IF;

  -- Get current year prices
  WITH
    "Extras" AS (
      SELECT r.id,
        EXP(SUM(LN(1 + COALESCE(rat."Increment", 0) / 100))) AS "Extra"
      FROM "Resource"."Resource" r
        LEFT JOIN "Resource"."Resource_amenity" ra ON ra."Resource_id" = r.id 
        LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
      GROUP BY 1
    ),
    "Prices" AS (
      SELECT r.id,
        r."Billing_type",
        CASE
          WHEN months < 3 THEN pd."Rent_short" * pr."Multiplier"
          WHEN months < 7 THEN pd."Rent_medium" * pr."Multiplier"
          ELSE pd."Rent_long" * pr."Multiplier"
        END AS "Rent",
        pd."Services",
        pd."Deposit",
        pd."Final_cleaning",
        pd."Second_resident",
        pd."Limit"
      FROM "Resource"."Resource" r
        INNER JOIN "Billing"."Pricing_detail" pd 
          ON pd."Building_id" = r."Building_id"
          AND pd."Flat_type_id" = r."Flat_type_id" 
          AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
        INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id" 
      WHERE pd."Year" = YEAR
        AND r.id = NEW."Resource_id"
    )
  SELECT 
    p."Billing_type",
    ROUND(p."Rent" * e."Extra") AS "Rent",
    p."Services",
    p."Deposit",
    p."Final_cleaning",
    p."Second_resident",
    p."Limit"
  INTO billing_type, rent, services, deposit, final_cleaning, second_resident, limit
  FROM "Prices" p
  LEFT JOIN "Extras" e ON p.id = e.id;
  
  -- Get next year prices
  WITH
    "Extras" AS (
      SELECT r.id,
        EXP(SUM(LN(1 + COALESCE(rat."Increment", 0) / 100))) AS "Extra"
      FROM "Resource"."Resource" r
        LEFT JOIN "Resource"."Resource_amenity" ra ON ra."Resource_id" = r.id 
        LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
      GROUP BY 1
    ),
    "Prices" AS (
      SELECT r.id,
        CASE
          WHEN months < 3 THEN pd."Rent_short" * pr."Multiplier"
          WHEN months < 7 THEN pd."Rent_medium" * pr."Multiplier"
          ELSE pd."Rent_long" * pr."Multiplier"
        END AS "Rent",
        pd."Services"
      FROM "Resource"."Resource" r
        INNER JOIN "Billing"."Pricing_detail" pd 
          ON pd."Building_id" = r."Building_id"
          AND pd."Flat_type_id" = r."Flat_type_id" 
          AND COALESCE(pd."Place_type_id", 0) = COALESCE(r."Place_type_id", 0)
        INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id" 
      WHERE pd."Year" = YEAR + 1
        AND r.id = NEW."Resource_id"
    )
  SELECT 
    ROUND(COALESCE(p."Rent", rent) * e."Extra", 0) AS "Rent",
    COALESCE(p."Services", services, 0)
  INTO n_rent, n_services
  FROM "Prices" p
  LEFT JOIN "Extras" e ON p.id = e.id;

  -- Base values
  NEW."Deposit"          := COALESCE(NEW."Deposit", deposit, rent + second_resident + services, 0);
  NEW."Final_cleaning"   := COALESCE(NEW."Final_cleaning", final_cleaning, 0);
  NEW."Limit"            := COALESCE(NEW."Limit", "limit", 0);
  IF NEW."New_check_out" < NEW."Date_to" THEN
    NEW."Rent"           := COALESCE(NEW."Rent", rent + second_resident, 0);
    NEW."Services"       := COALESCE(NEW."Services", services, 0);
  ELSE
    NEW."Rent"           := COALESCE(rent + second_resident, NEW."Rent", 0);
    NEW."Services"       := COALESCE(services, NEW."Services", 0);
  END IF;
 
  -- Prices
  monthly_rent     := NEW."Rent";
  monthly_services := NEW."Services";
  n_rent           := COALESCE(n_rent, NEW."Rent");
  n_services       := COALESCE(n_services, NEW."Services");

  -- Loop to insert prices
  dt_curr = NEW."Date_from";
  dt_to = dt_to + INTERVAL '1 day';
  WHILE dt_curr < dt_to LOOP

    -- Year change?
    IF EXTRACT(MONTH FROM dt_curr) > 8 OR EXTRACT(YEAR FROM dt_curr) > EXTRACT(YEAR FROM NEW."Date_from") THEN
      monthly_rent     := ROUND(n_rent, 0);
      monthly_services := ROUND(n_services, 0);
    END IF; 
 
    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);
 
    -- Complete months
    curr_rent     := monthly_rent;
    curr_services := monthly_services;

    -- Incomplete months
    dt_intr := AGE(dt_next, dt_curr);
    IF dt_intr < INTERVAL '1 month' THEN
     
      IF billing_type = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          curr_rent := ROUND(monthly_rent / 2, 1);
          curr_services := ROUND(monthly_services / 2, 1);
        END IF;
      END IF;
   
      IF billing_type = 'proporcional' THEN
        days := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        curr_rent := ROUND(monthly_rent * EXTRACT(DAY FROM dt_intr) / days, 1);
        curr_services := ROUND(monthly_services * EXTRACT(DAY FROM dt_intr) / days, 1);
      END IF;

    END IF;

    -- Insert price
    INSERT INTO "Booking"."Booking_price"
      ("Booking_id", "Rent_date", "Rent", "Services", "Rent_total", "Services_total", "Rent_rack", "Services_rack")
      VALUES (NEW.id, dt_curr, curr_rent, curr_services, curr_rent, curr_services, monthly_rent, monthly_services)
      ON CONFLICT ("Booking_id", "Rent_date") DO NOTHING;
 
    -- Next month
    dt_curr := date_trunc('month', dt_curr) + interval '1 month';
 
  END LOOP; 

  -- Not ECO/EXT
  IF NEW."New_check_out" IS NULL OR NEW."New_check_out" = NEW."Date_to" THEN
    RETURN NEW;
  END IF;

  -- ECO/EXT, update dates
  SELECT SUM("Rent") INTO curr_total FROM "Booking"."Booking_price" WHERE "Booking_id" = NEW.id;
  NEW."Old_check_out" := NEW."Date_to";
  NEW."Date_to" := NEW."New_check_out";
  NEW."Eco_ext_change_ok" := FALSE;
  IF curr_total = prev_total THEN
    NEW."New_check_out" := NULL;
  ELSE
    NEW."Check_out" := NULL;
  END IF;
  RETURN NEW;

END;
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

  monthly_rent NUMERIC;
  monthly_services NUMERIC;

  prev_total NUMERIC;
  curr_total NUMERIC;

BEGIN

  -- Date to
  dt_to = NEW."Date_to";

  -- No resource, ignore
  IF NEW."Resource_id" IS NULL THEN
    RETURN NEW;
  END IF;

  -- Not ECO_EXT?
  IF NEW."New_check_out" IS NULL OR NEW."New_check_out" = NEW."Check_out" OR NEW."New_check_out" = NEW."Date_to" THEN

    -- Not yet confirmed, ignore
    IF NEW."Status" NOT IN ('solicitud', 'solicitudpagada', 'alternativas', 'alternativaspagada', 'pendientepago') THEN
      RETURN NEW;
    END IF;

    -- Dates and resource not changed, ignore
    IF NEW."Resource_id" = OLD."Resource_id" AND NEW."Date_from" = OLD."Date_from" AND NEW."Date_to" = OLD."Date_to" THEN
      RETURN NEW;
    END IF;

  -- ECO/EXT
  ELSE

    -- Update dates
    dt_to := NEW."New_check_out";
   
    -- Get previous accumulated rent
    SELECT SUM("Rent") INTO prev_total FROM "Booking"."Booking_price" WHERE "Booking_id" = NEW.id;

    -- Delete not billed last prices
    DELETE FROM "Booking"."Booking_price"
    WHERE "Booking_id" = NEW.id 
      AND "Invoice_rent_id" IS NULL
      AND "Invoice_services_id" IS NULL
      AND "Rent_date" >= date_trunc('month', LEAST(NEW."New_check_out", NEW."Date_to"));
 
  END IF;

  -- Calculate stay length in montns
  SELECT EXTRACT(MONTH FROM AGE(dt_to, NEW."Date_from")) INTO months;

  -- Calculate year
  SELECT EXTRACT(YEAR FROM NEW."Date_from") INTO year;
  IF EXTRACT(MONTH FROM dt_curr) > 8 THEN
    year := year + 1;
  END IF;

  -- Get prices
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
        END as "Rent",
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
    ROUND(p."Rent" * e."Extra") as "Rent",
    COALESCE(p."Services", 0),
    COALESCE(p."Deposit", 0),
    COALESCE(p."Final_cleaning", 0),
    COALESCE(p."Second_resident", 0),
    COALESCE(p."Limit", 0)
  INTO billing_type, rent, services, deposit, final_cleaning, second_resident, limit
  FROM "Prices" p
  LEFT JOIN "Extras" e ON p.id = e.id;

  -- Base values
  rent := rent + second_resident;
  NEW."Deposit" := GREATEST(deposit, rent + services);
  NEW."Rent" := rent;
  NEW."Services" := services;
  NEW."Final_cleaning" := final_cleaning;
  NEW."Limit" := "limit";

  -- Loop to insert prices
  dt_curr = NEW."Date_from";
  dt_to = dt_to + INTERVAL '1 day';
  WHILE dt_curr < dt_to LOOP

    -- Prices
    monthly_rent := rent;
    monthly_services := services;

    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);
 
    -- Incomplete months
    dt_intr := AGE(dt_next, dt_curr);
    IF dt_intr < INTERVAL '1 month' THEN
     
      IF billing_type = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          monthly_rent := ROUND(monthly_rent / 2, 1);
          monthly_services := ROUND(monthly_services / 2, 1);
        END IF;
      END IF;
   
      IF billing_type = 'proporcional' THEN
        days := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        monthly_rent := ROUND(monthly_rent * EXTRACT(DAY FROM dt_intr) / days, 1);
        monthly_services := ROUND(monthly_services * EXTRACT(DAY FROM dt_intr) / days, 1);
      END IF;
   
    END IF;
   
    -- Final cleaning
    IF date_trunc('month', dt_curr) + interval '1 month' >= dt_to THEN
      monthly_services := ROUND(monthly_services + final_cleaning, 0);
    END IF;

    -- Insert price
    INSERT INTO "Booking"."Booking_price"
      ("Booking_id", "Rent_date", "Rent", "Services", "Rent_total", "Services_total")
      VALUES (NEW.id, dt_curr, monthly_rent, monthly_services, monthly_rent, monthly_services)
      ON CONFLICT ("Booking_id", "Rent_date") DO NOTHING;
 
    -- Next month
    dt_curr := date_trunc('month', dt_curr) + interval '1 month';
 
  END LOOP; 

  -- ECO/EXT, update dates
  IF NEW."New_check_out" IS NOT NULL THEN
    SELECT SUM("Rent") INTO curr_total FROM "Booking"."Booking_price" WHERE "Booking_id" = NEW.id;
    IF curr_total <> prev_total THEN
      NEW."Old_check_out" := COALESCE(NEW."Check_out", NEW."Date_to");
      NEW."Date_to" := dt_to - INTERVAL '1 day';
    ELSE
      NEW."New_check_out" := NULL;
    END IF;
  END IF;


  -- Return
  RETURN NEW;

END;
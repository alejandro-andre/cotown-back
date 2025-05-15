-- Calcula los precios de la reserva
DECLARE

  curr_user VARCHAR;

  promotion RECORD;

  dias INTEGER;
  months INTEGER;
  ano INTEGER;
  n_ano INTEGER;
 
  dt_to DATE;
  dt_curr DATE;
  dt_next DATE;
  dt_intr INTERVAL;

  rent NUMERIC;
  services NUMERIC;
  deposit NUMERIC;
  deposit_base NUMERIC;
  final_cleaning NUMERIC;
  second_resident NUMERIC;
  climit NUMERIC;

  n_rent NUMERIC;
  n_services NUMERIC;

  monthly_rent NUMERIC;
  monthly_services NUMERIC;

  disc_type INTEGER;
  disc_rent NUMERIC;
  disc_services NUMERIC;

  curr_rent NUMERIC;
  curr_services NUMERIC;

  prev_total NUMERIC;
  curr_total NUMERIC;

BEGIN

  -- Date to
  dt_to = NEW."Date_to";

  -- Status
  IF NEW."Status" IN ('descartada','descartadapagada','cancelada','caducada','finalizada') THEN
    RETURN NEW;
  END IF;

  -- No resource, ignore
  IF NEW."Resource_id" IS NULL THEN
    NEW."Deposit"        := NULL;
    NEW."Rent"           := NULL;
    NEW."Services"       := NULL;
    NEW."Final_cleaning" := NULL;
    NEW."Limit"          := NULL;
    RETURN NEW;
  END IF;

  -- Look up promotion
  SELECT *
  INTO promotion
  FROM "Billing"."Promotion"
  WHERE id = NEW."Promotion_id";

  -- Check if promotion still applicable
  -- ...

  -- Not ECO_EXT?
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
  SELECT EXTRACT(YEAR FROM NEW."Date_from") INTO ano;
  IF EXTRACT(MONTH FROM NEW."Date_from") > 8 THEN
    ano := ano + 1;
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
      WHERE pd."Year" = ano
        AND r.id = NEW."Resource_id"
    )
  SELECT 
    ROUND(p."Rent" * e."Extra") AS "Rent",
    p."Services",
    p."Deposit",
    p."Final_cleaning",
    p."Second_resident",
    p."Limit"
  INTO rent, services, deposit, final_cleaning, second_resident, climit
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
      WHERE pd."Year" = ano + 1
        AND r.id = NEW."Resource_id"
    )
  SELECT 
    ROUND(COALESCE(p."Rent", rent) * e."Extra", 0) AS "Rent",
    COALESCE(p."Services", services, 0)
  INTO n_rent, n_services
  FROM "Prices" p
  LEFT JOIN "Extras" e ON p.id = e.id;

  -- Base values
  deposit_base := ROUND((rent + second_resident + services) * 1.5);
  NEW."Deposit" := COALESCE(NEW."Deposit", deposit, deposit_base);
  IF NEW."Deposit" < deposit_base THEN
    NEW."Deposit" = deposit_base;
  END IF;
  NEW."Final_cleaning" := COALESCE(NEW."Final_cleaning", final_cleaning, 0);
  NEW."Limit"          := COALESCE(NEW."Limit", climit, 0);
  IF NEW."New_check_out" < NEW."Date_to" THEN
    NEW."Rent"         := COALESCE(NEW."Rent", rent + second_resident, 0);
    NEW."Services"     := COALESCE(NEW."Services", services, 0);
  ELSE
    NEW."Rent"         := COALESCE(rent + second_resident, NEW."Rent", 0);
    NEW."Services"     := COALESCE(services, NEW."Services", 0);
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
    SELECT EXTRACT(YEAR FROM dt_curr) INTO n_ano;
    IF EXTRACT(MONTH FROM dt_curr) > 8 THEN
      n_ano := n_ano + 1;
    END IF;
    IF n_ano > ano THEN
      monthly_rent     := ROUND(n_rent, 0);
      monthly_services := ROUND(n_services, 0);
    END IF; 
 
    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);
 
    -- Base prices
    curr_rent     := monthly_rent;
    curr_services := monthly_services;
    disc_rent     := 0;
    disc_services := 0;
    disc_type     := NULL;

    -- Base promotion
    IF dt_curr >= promotion."Date_from" AND dt_curr <= promotion."Date_to" THEN
      IF promotion."Value_rent" IS NOT NULL THEN
        disc_rent := promotion."Value_rent";
        disc_type := 1;
      ELSE
        IF promotion."Value_rent_pct" IS NOT NULL THEN
          disc_rent     := curr_rent * (promotion."Value_rent_pct" / 100);
          disc_services := curr_services * (promotion."Value_rent_pct" / 100);
          disc_type     := 1;
        END IF;
      END IF;
    END IF;

    -- Incomplete months
    dt_intr := AGE(dt_next, dt_curr);
    IF dt_intr < INTERVAL '1 month' THEN
     
      IF NEW."Billing_type" = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          disc_rent     := ROUND(disc_rent / 2, 1);
          disc_services := ROUND(disc_services / 2, 1);
          curr_rent     := ROUND(monthly_rent / 2, 1);
          curr_services := ROUND(monthly_services / 2, 1);
        END IF;
      END IF;
   
      IF NEW."Billing_type" = 'proporcional' THEN
        dias := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        disc_rent     := ROUND(disc_rent * EXTRACT(DAY FROM dt_intr) / dias, 1);
        disc_services := ROUND(disc_services * EXTRACT(DAY FROM dt_intr) / dias, 1);
        curr_rent     := ROUND(monthly_rent * EXTRACT(DAY FROM dt_intr) / dias, 1);
        curr_services := ROUND(monthly_services * EXTRACT(DAY FROM dt_intr) / dias, 1);
      END IF;

    END IF;

    -- Insert price
    INSERT INTO "Booking"."Booking_price"
      ("Booking_id", "Rent_date", "Rent", "Services", "Rent_discount", "Services_discount", "Rent_rack", "Services_rack", "Discount_type_id")
      VALUES (NEW.id, dt_curr, curr_rent, curr_services, disc_rent, disc_services, monthly_rent, monthly_services, disc_type)
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
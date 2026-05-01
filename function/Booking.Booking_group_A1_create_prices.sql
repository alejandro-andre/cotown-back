-- Inserta las mensualidades
DECLARE

  dt_to DATE;
  dt_curr DATE;
  dt_next DATE;
  dt_intr INTERVAL;
  num INTEGER;
  resource RECORD;

  dias INTEGER;
  rent NUMERIC;
  services NUMERIC;
  effective_billing_type VARCHAR;

BEGIN

  -- Only calc if not master
  IF NEW."Master" THEN
    RETURN NEW;
  END IF;

  -- Only calc if not yet confirmed or no calculated yet
  SELECT COUNT(*) 
  INTO num
  FROM "Booking"."Booking_group_price"
  WHERE "Booking_id" = NEW.id;
  IF (num > 0 AND NEW."Rent" = OLD."Rent") OR NEW."Status" <> 'grupobloqueado' THEN
    RETURN NEW;
  END IF;

  -- Borra viejos fuera de los margenes del contrato
  DELETE FROM "Booking"."Booking_group_price"
  WHERE "Booking_id" = NEW.id
  AND ("Rent_date" < NEW."Date_from" OR "Rent_date" > NEW."Date_to");

  -- Loop to insert prices
  dt_curr = NEW."Date_from";
  dt_to = NEW."Date_to" + INTERVAL '1 day';
  WHILE dt_curr < dt_to LOOP
    -- End of period (first day next month or last day + 1)
    dt_next := LEAST(date_trunc('month', dt_curr) + INTERVAL '1 month', dt_to);

    -- Incomplete months
    rent     := NEW."Rent";
  	services := NEW."Services";
    dt_intr := AGE(dt_next, dt_curr);
    IF dt_intr < INTERVAL '1 month' THEN

      -- First or last month
      IF dt_next = dt_to AND NEW."Billing_type_last" IS NOT NULL THEN
        effective_billing_type := NEW."Billing_type_last";
      ELSE
        effective_billing_type := NEW."Billing_type";
      END IF;

      IF NEW."Billing_type" = 'quincena' THEN
        IF EXTRACT(DAY FROM dt_curr) >= 15 OR EXTRACT(DAY FROM (dt_next - INTERVAL '1 day')) < 15 THEN
          rent     := ROUND(NEW."Rent" / 2, 1);
          services := ROUND(NEW."Services" / 2, 1);
        END IF;
      END IF;
      IF NEW."Billing_type" = 'proporcional' THEN
        dias     := EXTRACT(DAY FROM date_trunc('month', dt_curr + INTERVAL '1 month' - INTERVAL '1 day') - INTERVAL '1 day');
        rent     := ROUND(NEW."Rent" * EXTRACT(DAY FROM dt_intr) / dias, 1);
        services := ROUND(NEW."Services" * EXTRACT(DAY FROM dt_intr) / dias, 1);
      END IF;

    END IF;

    INSERT INTO "Booking"."Booking_group_price" ("Booking_id", "Rent_date", "Rent", "Services", "Expenses", "Utility", "Furniture") 
    VALUES (NEW.id, dt_curr, rent, services, NEW."Expenses", NEW."Limit", NEW."Furniture")
	ON CONFLICT ("Booking_id", "Rent_date") DO UPDATE SET
  	  "Rent"      = EXCLUDED."Rent",
      "Services"  = EXCLUDED."Services",
      "Expenses"  = EXCLUDED."Expenses",
      "Utility"   = EXCLUDED."Utility",
      "Furniture" = EXCLUDED."Furniture";
    dt_curr := date_trunc('month', dt_curr) + INTERVAL '1 month';

  END LOOP;

  -- Return
  RETURN NEW;

END;
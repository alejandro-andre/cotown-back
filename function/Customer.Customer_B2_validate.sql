-- Verifica el cliente
DECLARE

  tutor_id INTEGER;
  customer_age INTEGER;

BEGIN

  -- Obtiene la edad
  IF NEW."Birth_date" < '1910-01-01' THEN
    NEW."Birth_date" = NULL;
    RETURN NEW;
  END IF;
  SELECT DATE_PART('year', AGE(NOW(), NEW."Birth_date")) INTO customer_age;

  -- Menor?
  IF customer_age < 18 THEN
    IF NEW."Tutor_id" IS NULL THEN 
      RAISE EXCEPTION '!!!Minor require tutor!!!Menores requieren tutor!!!';
    ELSE 
      SELECT DATE_PART('year', AGE(NOW(), "Birth_date"))
        INTO customer_age
        FROM "Customer"."Customer"
        WHERE id = NEW."Tutor_id";
      IF customer_age < 18 THEN
          RAISE EXCEPTION '!!!Tutor must be > 18 years!!!El tutor debe tener más de 18 años!!!';
      END IF;
    END IF;
  END IF;

  -- Cambio de email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
  	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";
    IF num > 0 THEN
      RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
    END IF;
    UPDATE "Models"."User" SET email = NEW."Email" WHERE username = NEW."User_name";
  END IF;

  -- Ok
  RETURN NEW;
  
END;
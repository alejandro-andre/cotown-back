-- Verifica el cliente
DECLARE

  tutor_id INTEGER;
  customer_age INTEGER;

BEGIN

  -- No permite cambiar el email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
    RAISE EXCEPTION '!!!Email cannot be changed!!!No se puede cambiar el email!!!';
  END IF;

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

  -- Ok
  RETURN NEW;
  
END;
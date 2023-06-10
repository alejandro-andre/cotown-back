-- Verifica el cliente
DECLARE

  customer_age INTEGER;
  num INTEGER;

BEGIN

  -- Obtiene la edad
  IF NEW."Birth_date" < '1910-01-01' THEN
    NEW."Birth_date" = NULL;
    RETURN NEW;
  END IF;
  SELECT DATE_PART('year', AGE(NOW(), NEW."Birth_date")) INTO customer_age;

  -- Menor?
  IF customer_age > 17 THEN
    IF NEW."Tutor_id_type_id" IS NULL OR NEW."Tutor_document" IS NULL OR 
       NEW."Tutor_name" IS NULL OR (NEW."Tutor_email" IS NULL AND NEW."Tutor_phones" IS NULL) THEN 
      RAISE EXCEPTION '!!!Minor require tutor!!!Menores requieren tutor!!!';
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
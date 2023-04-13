-- Verifica si el residente es menor y necesita un tutor
DECLARE
  tutor_id INTEGER;
  customer_age INTEGER;

BEGIN
  -- Select customer
  SELECT DATE_PART('year', AGE(NOW(), NEW."Birth_date")) INTO customer_age;

  -- Minor?
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
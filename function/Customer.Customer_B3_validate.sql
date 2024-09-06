-- Verifica el cliente
DECLARE

  customer_age INTEGER;
  curr_user VARCHAR;
  num INTEGER;

BEGIN

  -- Quita espacios y caracteres especiales
  NEW."IBAN" = UPPER(TRIM(REGEXP_REPLACE(NEW."IBAN", '[^a-zA-Z0-9]', '', 'g')));
  
  -- Obtiene la edad
  IF NEW."Birth_date" < '1910-01-01' THEN
    NEW."Birth_date" = NULL;
    RETURN NEW;
  END IF;
  SELECT DATE_PART('year', AGE(NOW(), NEW."Birth_date")) INTO customer_age;

  -- Menor?
  IF customer_age < 18 THEN
    IF NEW."Tutor_id_type_id" IS NULL OR NEW."Tutor_document" IS NULL OR
       NEW."Tutor_name" IS NULL OR (NEW."Tutor_email" IS NULL AND NEW."Tutor_phones" IS NULL) THEN
      RAISE EXCEPTION '!!!Minor require tutor!!!Menores requieren tutor!!!';
    END IF;
  END IF;

  -- IBAN/SEPA
  IF NEW."IBAN" IS NOT NULL AND NEW."IBAN" <> '' THEN
    IF NOT EXISTS (SELECT id FROM "Geo"."Country" WHERE "Code" = upper(substring(trim(NEW."IBAN"), 1, 2)) AND "Sepa" = TRUE) THEN
      RAISE EXCEPTION '!!!IBAN from non-SEPA country!!!IBAN de un país no-SEPA!!!';
    END IF;
  END IF;

  -- Same account
  IF NEW."IBAN" IS NOT NULL AND NEW."IBAN" <> '' AND NEW."Same_account" THEN
    NEW."Bank_account"    = NEW."IBAN";
    NEW."Swift"           = NULL;
    NEW."Bank_holder"     = NULL;
    NEW."Bank_name"       = NULL;
    NEW."Bank_address"    = NULL;
    NEW."Bank_city"       = NULL;
    NEW."Bank_country_id" = NULL;
  ELSE
    NEW."Same_account" = FALSE;
  END IF;

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 

  -- Documentos obligatorios
  IF TG_OP = 'UPDATE' THEN
    INSERT INTO "Customer"."Customer_doc" ("Customer_id", "Customer_doc_type_id")
      SELECT NEW.id, id
      FROM "Customer"."Customer_doc_type" cdt
      WHERE "Mandatory" = TRUE
      AND cdt."Id_type_id" = NEW."Id_type_id"
    ON CONFLICT ("Customer_id", "Customer_doc_type_id") DO NOTHING;
  END IF;

  -- Cambio de email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
  	SELECT COUNT(*) INTO num FROM "Models"."User" WHERE email = NEW."Email";
    IF num > 0 THEN
      EXECUTE 'SET ROLE "' || curr_user || '"';
      RAISE EXCEPTION '!!!Email already exists!!!El email ya existe!!!';
    END IF;
    UPDATE "Models"."User" SET email = NEW."Email" WHERE username = NEW."User_name";
  END IF;

  -- Ok
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;
 
END;
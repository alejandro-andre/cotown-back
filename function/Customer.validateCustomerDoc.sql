DECLARE
  num INTEGER;
  
BEGIN
  -- Verifica que se adjunta el numero de imágenes necesarias
  SELECT "Images"
  INTO num
  FROM "Customer"."Customer_doc_type" cd
  WHERE id = NEW."Customer_doc_type_id";
  IF num > 1 AND NEW."Document_back" IS NULL THEN
    RAISE EXCEPTION '!!!Please, insert two images for this documento!!!Por favor, incluye dos imagenes en este documento!!!';
  END IF;

  -- Validates that the expiry date of a document is greater than the current date. validateCustomerDocDateExpiryDate
  IF NEW."Expiry_date" IS NOT NULL THEN
    IF NEW."Expiry_date" < current_date THEN
      RAISE EXCEPTION '!!!The expiry date must be greater or equal than the current day.!!!La fecha de expiracion debe ser mayor o igual al día actual.!!!';
    END IF;
  END IF;

  RETURN NEW;

END;
-- Documentos obligatorios
-- AFTER INSERT/UPDATE
DECLARE

  curr_user VARCHAR;
  id_type_id INTEGER;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  SELECT c."Id_type_id" 
  INTO id_type_id 
  FROM "Customer"."Customer" c 
  WHERE c.id = NEW."Customer_id";
  
  -- Documentos id obligatorios
  INSERT INTO "Customer"."Customer_doc" ("Customer_id", "Customer_doc_type_id")
    SELECT NEW."Customer_id", cdt.id
    FROM "Customer"."Customer_doc_type" cdt
    WHERE (cdt."Id_type_id" = id_type_id)
      AND NOT EXISTS (
        SELECT 1
        FROM "Customer"."Customer_doc" cd
        WHERE cd."Customer_id"          = NEW."Customer_id"
          AND cd."Customer_doc_type_id" = cdt.id
      );
 
  -- Documentos motivo obligatorios
  INSERT INTO "Customer"."Customer_doc" ("Customer_id", "Customer_doc_type_id", "Booking_id")
    SELECT NEW."Customer_id", cdt.id, NEW.id
    FROM "Customer"."Customer_doc_type" cdt
    WHERE cdt."Mandatory" 
      AND (cdt."Reason_id" = NEW."Reason_id")
      AND NOT EXISTS (
        SELECT 1
        FROM "Customer"."Customer_doc" cd
        WHERE cd."Customer_id"          = NEW."Customer_id"
          AND cd."Customer_doc_type_id" = cdt.id
          AND cd."Booking_id"           = NEW.id
      );

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
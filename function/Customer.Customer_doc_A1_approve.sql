-- Valida la aprobación de los documentos de cliente
DECLARE

  curr_user VARCHAR;
  docs_ok BOOLEAN;
  status VARCHAR;
  c INTEGER;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 

  -- Status del booking
  SELECT "Status" INTO status FROM "Booking"."Booking" b WHERE b.id = NEW."Booking_id";
  IF status <> 'confirmada' THEN
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- ¿No hay documentos, o hay al menos uno aprobado?
  SELECT
    NOT EXISTS (
      SELECT 1 FROM "Customer"."Customer_doc" cd WHERE cd."Booking_id" = NEW."Booking_id"
    )
    OR EXISTS (
      SELECT 1 FROM "Customer"."Customer_doc" cd WHERE cd."Booking_id" = NEW."Booking_id" AND cd."Approved" IS TRUE
    )
    OR NEW."Approved" IS TRUE
  INTO docs_ok;
  
  -- Actualiza
  IF docs_ok THEN
    UPDATE "Booking"."Booking" SET "Status" = 'documentacionok' WHERE id = NEW."Booking_id";
  END IF;

  -- Fin
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
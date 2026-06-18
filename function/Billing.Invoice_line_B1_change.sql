-- Verifica si se puede modificar la factura
-- AFTER INSERT/UPDATE/DELETE
DECLARE

  issued BOOLEAN;
  tax_id INTEGER;
  invoice_id INTEGER;
  booking_id INTEGER;
  booking_group_id INTEGER;
  resource_id INTEGER;
  provider_id INTEGER;
  concept VARCHAR;

BEGIN

  -- Invoice id
  IF TG_OP = 'DELETE' THEN
  	invoice_id = OLD."Invoice_id";
  ELSE
  	invoice_id = NEW."Invoice_id";
  END IF;

  -- Get invoice info
  SELECT "Issued", "Provider_id", "Booking_id", "Booking_group_id" 
  INTO issued, provider_id, booking_id, booking_group_id 
  FROM "Billing"."Invoice" 
  WHERE id = invoice_id;

  -- Issued? Cannot change
  IF issued AND (
     OLD."Amount"     <> NEW."Amount"     OR
     OLD."Comments"   <> NEW."Comments"   OR
     OLD."Concept"    <> NEW."Concept"    OR
     OLD."Product_id" <> NEW."Product_id" OR
     OLD."Tax_id"     <> NEW."Tax_id"
    ) THEN
    RAISE EXCEPTION '!!!Bill has been already issued, cannot change!!!La factura ya ha sido emitida, no puede cambiarse!!!';
  END IF;

  -- Delete
  IF TG_OP = 'DELETE' THEN
    IF issued THEN
      RAISE EXCEPTION '!!!Bill has been already issued, cannot change!!!La factura ya ha sido emitida, no puede cambiarse!!!';
    END IF;
    RETURN OLD;
  END IF;

  -- Resource
  IF NEW."Resource_id" IS NULL THEN
    IF booking_id IS NOT NULL THEN
      SELECT CASE WHEN r."Flat_id" IS NULL THEN r.id ELSE r."Flat_id" END
      INTO resource_id
      FROM "Booking"."Booking" b
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      WHERE b.id = booking_id;
      NEW."Resource_id" = resource_id;
    ELSE
      RAISE EXCEPTION '!!!Resource (flat) is mandatory!!!El recurso (piso) es obligatorio!!!';
    END IF;
  END IF;

  -- Management fee (según frecuencia de limpieza)
  IF provider_id <> 1 AND NEW."Management_fee" IS NULL THEN
    IF booking_id IS NOT NULL THEN
      SELECT
        CASE
          WHEN b."Cleaning_freq" = 'no'        THEN r."Management_fee_no_cleaning"
          WHEN b."Cleaning_freq" = 'semanal'   THEN r."Management_fee_weekly"
          WHEN b."Cleaning_freq" = 'quincenal' THEN r."Management_fee_biweekly"
          WHEN b."Cleaning_freq" = 'mensual'   THEN r."Management_fee_monthly"
          WHEN b."Cleaning_freq" = 'sin'       THEN r."Management_fee"
          ELSE r."Management_fee_biweekly"
        END
      INTO NEW."Management_fee"
      FROM "Booking"."Booking" b
      JOIN "Resource"."Resource" r ON r.id = NEW."Resource_id"
      WHERE b.id = booking_id;
    END IF;
    IF booking_group_id IS NOT NULL THEN
      SELECT
        CASE
          WHEN b."Cleaning_freq" = 'no'        THEN r."Management_fee_no_cleaning"
          WHEN b."Cleaning_freq" = 'semanal'   THEN r."Management_fee_weekly"
          WHEN b."Cleaning_freq" = 'quincenal' THEN r."Management_fee_biweekly"
          WHEN b."Cleaning_freq" = 'mensual'   THEN r."Management_fee_monthly"
          WHEN b."Cleaning_freq" = 'sin'       THEN r."Management_fee"
          ELSE r."Management_fee_biweekly"
        END
      INTO NEW."Management_fee"
      FROM "Booking"."Booking_group" b
      JOIN "Resource"."Resource" r ON r.id = NEW."Resource_id"
      WHERE b.id = booking_group_id;
    END IF;
  END IF;

  -- Tax
  IF NEW."Tax_id" IS NULL THEN
    SELECT "Tax_id" INTO tax_id FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Tax_id" := tax_id;
  END IF;

  -- Concept
  IF NEW."Concept" IS NULL THEN
    SELECT "Name" INTO concept FROM "Billing"."Product" WHERE id = NEW."Product_id";
    NEW."Concept" := concept;
  END IF;

  -- Return
  RETURN NEW;

END;
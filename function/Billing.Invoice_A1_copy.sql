-- Copia las lineas de factura de otra
-- AFTER INSERT
BEGIN

  -- New invoice
  IF NEW."Duplicate_id" IS NULL THEN
    RETURN NEW;
  END IF;

  -- Duplicate invoice lines
  INSERT INTO "Billing"."Invoice_line" ("Invoice_id", "Product_id", "Amount", "Tax_id", "Concept", "Comments", "Resource_id")
    SELECT
      NEW.id,
      il."Product_id",
      il."Amount",
      il."Tax_id",
      il."Concept",
      il."Comments", 
      il."Resource_id"
    FROM "Billing"."Invoice_line" il 
    WHERE il."Invoice_id" = NEW."Duplicate_id";

  -- Clean field
  UPDATE "Billing"."Invoice" SET "Duplicate_id" = NULL WHERE id = NEW.id;

  -- Return
  RETURN NEW;

END;
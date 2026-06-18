-- Update Management_fee to NULL for invoice lines issued in the current month
DECLARE

  rec RECORD;

BEGIN

  FOR rec IN

    SELECT il.id, i."Code"
    FROM "Billing"."Invoice_line" il
    INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id"
    WHERE i."Issued" = TRUE
      AND DATE_TRUNC('month', i."Issued_date") = DATE_TRUNC('month', CURRENT_DATE)
      AND il."Management_fee" IS NOT NULL

  LOOP

    UPDATE "Billing"."Invoice_line"
    SET "Management_fee" = NULL
    WHERE id = rec.id;

    RAISE NOTICE 'Invoice_line: %, Invoice: %', rec.id, rec."Code";

  END LOOP;

END;

-- Additional services for final cleanings
DECLARE

  booking_id INTEGER;
  invoice_id INTEGER;
  rec RECORD;

BEGIN

  booking_id = 0;

  FOR rec IN

    -- Select not billed final cleanings from still unfinished bookings
	SELECT
	    bg.id,
	    bgr."Check_out",
	    r."Flat_id",
        f."Code",
	    bg."Payer_id",
        c."Payment_method_id",
	    COUNT(*) AS room_count,
	    bg."Final_cleaning" * COUNT(*) AS amount
	FROM "Booking"."Booking_group_rooming" bgr
	    INNER JOIN "Booking"."Booking_group" bg ON bg.id = bgr."Booking_id"
	    INNER JOIN "Booking"."Booking_group_rooms" br ON br.id = bgr."Room_id"
	    INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id"
	    INNER JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
        INNER JOIN "Customer"."Customer" c ON c.id = bg."Payer_id"
	WHERE bg."Final_cleaning" > 0
	  AND bgr."Check_out" <= CURRENT_DATE
	  AND bg."Status" IN ('inhouse', 'revision', 'devolvergarantia', 'finalizada')
	  AND COALESCE(bgr."Cleaning_billed", FALSE) = FALSE
	GROUP BY 1, 2, 3, 4, 5, 6
	ORDER BY 1, 2, 3

  LOOP

	-- Booking id change
	IF rec.id <> booking_id THEN

      -- Issue invoice
      IF booking_id <> 0 THEN
        UPDATE "Billing"."Invoice"
          SET "Issued" = TRUE
          WHERE "Booking_group_id" = booking_id
            AND "Bill_type" = 'factura'
            AND "Issued" = FALSE;
      END IF;

      -- Insert invoice
      INSERT INTO "Billing"."Invoice"
        ("Bill_type", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
      VALUES
        ('factura', 1, rec."Payer_id", rec.id, COALESCE(rec."Payment_method_id", 2), NULL, 'Limpieza final plazas con salida el ' || rec."Check_out")
      RETURNING id INTO invoice_id;
      RAISE NOTICE 'INSERT BILL % % %', rec.id, rec."Check_out", invoice_id;

	END IF;

	-- Insert line
  INSERT INTO "Billing"."Invoice_line" 
    ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept", "Resource_id")
  VALUES
    (invoice_id, rec.amount, 19, 1, 'Limpieza final ' || rec."Code" || ' - ' || rec.room_count || ' plazas', rec."Flat_id");
  RAISE NOTICE ' LINE % % %', rec."Flat_id", rec.room_count, rec.amount;

  -- Update checkout
	UPDATE "Booking"."Booking_group_rooming"
    SET "Cleaning_billed" = TRUE
  WHERE "Booking_id" = rec.id
    AND "Check_out" = rec."Check_out"
    AND COALESCE("Cleaning_billed", FALSE) = FALSE;

	-- Next record
	booking_id = rec.id;

  END LOOP;

  -- Issue last invoice
  IF booking_id <> 0 THEN
    UPDATE "Billing"."Invoice"
      SET "Issued" = TRUE
      WHERE "Booking_group_id" = booking_id
        AND "Bill_type" = 'factura'
        AND "Issued" = FALSE;
  END IF;

END;
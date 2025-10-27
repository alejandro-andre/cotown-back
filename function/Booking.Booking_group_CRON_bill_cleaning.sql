-- Additional services for final cleanings
DECLARE

  rec RECORD;

BEGIN

  FOR rec IN

    -- Select not billed final cleanings from still unfinished bookings
    SELECT
      bg.id AS booking_id,
      bg."Status",
      bgr."Check_out",
      COUNT(*) AS room_count,
      SUM(bg."Final_cleaning") AS total_amount
    FROM "Booking"."Booking_group_rooming" bgr
      INNER JOIN "Booking"."Booking_group" bg ON bg.id = bgr."Booking_id"
    WHERE bg."Final_cleaning" > 0
      AND bgr."Cleaning_billed" = FALSE
      AND bgr."Check_out" <= CURRENT_DATE
      AND bg."Status" IN ('inhouse', 'revision', 'devolvergarantia', 'finalizada')
    GROUP BY bg.id, bg."Status", bgr."Check_out"

  LOOP

    -- Insert additional services
    INSERT INTO "Booking"."Booking_group_service" (
      "Booking_id", "Billing_date_from", "Quantity", "Amount", "Provider_id", "Product_id", "Tax_id", "Concept"
    ) VALUES(
      rec.booking_id,         -- Booking_id
      rec."Check_out",        -- Billing_date_from
      rec.room_count,         -- Quantity
      rec.total_amount,       -- Amount
      1,                      -- Provider_id: COTOWN
      19,                     -- Product_id: FiInal cleaning
      1,                      -- Tax_id: VAT 21%
      'Limpieza final: ' || rec.room_count || ' plazas con salida el ' || rec."Check_out"
    );

    -- Update checkout
  	UPDATE "Booking"."Booking_group_rooming"
      SET "Cleaning_billed" = TRUE
    WHERE "Booking_id" = rec.booking_id
      AND "Check_out" = rec."Check_out"
      AND "Cleaning_billed" = FALSE;

  END LOOP;

END;
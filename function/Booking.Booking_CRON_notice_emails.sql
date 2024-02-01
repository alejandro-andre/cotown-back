-- Envio planificado de emails
DECLARE

  booking_id INTEGER;
  flat_id INTEGER;
  date_in DATE;
 
  -- Faltan menos de 2 dias para el checkin y no se ha enviado aviso a compañeros
  curs CURSOR FOR
    SELECT b.id, r."Flat_id", COALESCE(b."Check_in", b."Date_from") 
    FROM "Booking"."Booking" b 
      INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id" 
    WHERE r."Flat_id" IS NOT NULL
      AND NOT b."Check_in_notice_ok"
      AND b."Status" IN ('firmacontrato','checkinconfirmado')
      AND COALESCE(b."Check_in", b."Date_from") <= (CURRENT_DATE + INTERVAL '2 days');

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO booking_id, flat_id, date_in;
  WHILE (FOUND) LOOP

    -- Notice roommates (inhouse)
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      SELECT c.id, 'compis', booking_id
      FROM "Booking"."Booking" b
        INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      WHERE b.id <> booking_id
        AND r."Flat_id" = flat_id
        AND b."Status" = 'inhouse'
        AND COALESCE(b."Check_in", b."Date_from") <= date_in
        AND COALESCE(b."Check_out", b."Date_to") > date_in;
    UPDATE "Booking"."Booking" b 
      SET "Check_in_notice_ok" = TRUE
      WHERE b.id = booking_id;

    FETCH curs INTO booking_id, flat_id, date_in;
  END LOOP;
  CLOSE curs;

END;

-- Envio planificado de emails
DECLARE

  rec_id INTEGER;
  flat_id INTEGER;
  date_in DATE;
 
  -- Faltan menos de 2 dias para el checkin y no se ha enviado aviso a compañeros
  curs CURSOR FOR
    SELECT b.id, r."Flat_id", b."Check_in"
    FROM "Booking"."Booking_group_rooming" b
      INNER JOIN "Booking"."Booking_group_rooms" br ON br.id = b."Room_id"
      INNER JOIN "Booking"."Booking_group" bg ON bg.id = b."Booking_id"
      INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id" 
    WHERE r."Flat_id" IS NOT NULL
      AND NOT b."Check_in_notice_ok"
      AND bg."Status" IN ('grupoconfirmado','inhouse')
      AND b."Check_in" <= (CURRENT_DATE + INTERVAL '2 days')
      AND bg."Type_B2C";

BEGIN

  RESET ROLE;

  OPEN curs;
  FETCH curs INTO rec_id, flat_id, date_in;
  WHILE (FOUND) LOOP

    -- Notice B2C roommates (inhouse)
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      SELECT c.id, 'compis', rec_id
      FROM "Booking"."Booking" b
        INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      WHERE r."Flat_id" = flat_id
        AND b."Status" = 'inhouse'
        AND COALESCE(b."Check_in", b."Date_from") <= date_in
        AND COALESCE(b."Check_out", b."Date_to") > date_in
      ;

    -- Notice B2B roommates (inhouse)
    INSERT
      INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id")
      SELECT c.id, 'compis', rec_id
      FROM "Booking"."Booking_group_rooming" b
        INNER JOIN "Booking"."Booking_group_rooms" br ON br.id = b."Room_id"
        INNER JOIN "Booking"."Booking_group" bg ON bg.id = b."Booking_id"
        INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
        INNER JOIN "Customer"."Customer" c ON c.id = bg."Payer_id"
      WHERE bg."Type_B2C" 
        AND r."Flat_id" = flat_id
        AND b."Status" = 'inhouse'
        AND b."Check_in" <= date_in
        AND b."Check_out" > date_in
        AND b.id <> rec_id;

    -- Update booking
    UPDATE "Booking"."Booking_group_rooming" b 
      SET "Check_in_notice_ok" = TRUE
      WHERE b.id = rec_id;

    FETCH curs INTO rec_id, flat_id, date_in;
  END LOOP;
  CLOSE curs;

END;

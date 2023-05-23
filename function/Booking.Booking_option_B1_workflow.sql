-- Gestiona las alternativas y modifica la solicitud
DECLARE

  booking_status VARCHAR;
  deposit_paid INTEGER;
  customer_id INTEGER;

BEGIN
  
  --RESET ROLE;
  
  -- ALTERNATIVAS a SOLICITUD
  -- ALTERNATIVASPAGADA A SOLICITUDPAGADA
  -- Aceptada, actualiza la petición
  IF NEW."Accepted" THEN
      UPDATE "Booking"."Booking"
      SET "Building_id" = NEW."Building_id", 
          "Flat_type_id" = NEW."Flat_type_id", 
          "Place_type_id" = NEW."Place_type_id",
          "Status" = CASE
            WHEN "Status" = 'alternativas' THEN 'solicitud'
            WHEN "Status" = 'alternativaspagada' THEN 'solicitudpagada'
            ELSE "Status"
          END
    WHERE id = NEW."Booking_id";
    RETURN NEW;
  END IF;

  -- Estado actual de la reserva
  SELECT "Status", "Customer_id" into booking_status, customer_id FROM "Booking"."Booking" WHERE "Booking".id = NEW."Booking_id";


  -- SOLICITUD a ALTERNATIVAS 
  -- Actualiza la solicitud
  IF booking_status = 'solicitud' THEN
     UPDATE "Booking"."Booking" SET "Status" = 'alternativas' WHERE id = NEW."Booking_id";
     INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'alternativas', NEW."Booking_id");
  END IF;

  -- SOLICITUDPAGADA a ALTERNATIVASPAGADA 
  -- Actualiza la solicitud pagada
  IF booking_status = 'solicitudpagada' THEN
    UPDATE "Booking"."Booking" SET "Status" = 'alternativaspagada' WHERE id = NEW."Booking_id";
    INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (customer_id, 'alternativas', NEW."Booking_id");
  END IF;

  -- Return
  RETURN NEW;

END;
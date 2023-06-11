-- Gestiona las alternativas y modifica la solicitud
DECLARE

  booking_status VARCHAR;
  deposit_paid INTEGER;
  customer_id INTEGER;
  curr_user VARCHAR;

BEGIN
  
  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 
 
  -- ALTERNATIVAS a SOLICITUD
  -- ALTERNATIVASPAGADA A SOLICITUDPAGADA
  -- Aceptada, actualiza la petición
  IF NEW."Accepted" THEN
      UPDATE "Booking"."Booking"
      SET "Building_id" = NEW."Building_id", 
          "Flat_type_id" = NEW."Flat_type_id", 
          "Place_type_id" = NEW."Place_type_id",
          "Button_options" = '',
          "Status" = CASE
            WHEN "Status" = 'alternativaspagada' THEN 'solicitudpagada'
            ELSE 'solicitud'
          END
    WHERE id = NEW."Booking_id";
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- Estado actual de la reserva
  SELECT "Status", "Customer_id" into booking_status, customer_id FROM "Booking"."Booking" WHERE "Booking".id = NEW."Booking_id";

  -- SOLICITUD a ALTERNATIVAS 
  -- Actualiza la solicitud
  IF booking_status = 'solicitud' THEN
       UPDATE "Booking"."Booking" 
       SET "Button_options" = CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW."Booking_id", '/status/alternativas')
       WHERE id = NEW."Booking_id";
  END IF;

  -- SOLICITUDPAGADA a ALTERNATIVASPAGADA 
  -- Actualiza la solicitud pagada
  IF booking_status = 'solicitudpagada' THEN
    UPDATE "Booking"."Booking" 
    SET "Button_options" = CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW."Booking_id", '/status/alternativaspagada')
    WHERE id = NEW."Booking_id";
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
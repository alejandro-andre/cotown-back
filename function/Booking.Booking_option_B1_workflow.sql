-- Gestiona las alternativas y modifica la solicitud
DECLARE

  booking_status VARCHAR;
  deposit_paid INTEGER;
  customer_id INTEGER;
  curr_user VARCHAR;
  button_options VARCHAR;
  new_options VARCHAR;

BEGIN
  
  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 
 
  -- Por defecto, deshabilita el boton
  new_options = '';

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
            WHEN "Status" = 'alternativas' THEN 'solicitud'
            ELSE "Status"
          END
    WHERE id = NEW."Booking_id";
    EXECUTE 'SET ROLE "' || curr_user || '"';
    RETURN NEW;
  END IF;

  -- Estado actual de la reserva
  SELECT "Status", "Customer_id", "Button_options"
  INTO booking_status, customer_id, button_options
  FROM "Booking"."Booking" 
  WHERE "Booking".id = NEW."Booking_id";

  -- SOLICITUD a ALTERNATIVAS 
  IF booking_status = 'solicitud' THEN
    new_options = CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW."Booking_id", '/status/alternativas');
  END IF;

  -- SOLICITUDPAGADA a ALTERNATIVASPAGADA 
  IF booking_status = 'solicitudpagada' THEN
    new_options = CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW."Booking_id", '/status/alternativaspagada');
  END IF;

  IF button_options <> new_options THEN
    UPDATE "Booking"."Booking" 
    SET "Button_options" = new_options
    WHERE id = NEW."Booking_id";
  END IF;

  -- Return
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
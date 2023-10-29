-- Gestiona las alternativas y modifica la solicitud
DECLARE

  curr_user VARCHAR;

BEGIN

  -- Check if has to send alternatives 
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- ALTERNATIVAS a SOLICITUD / ALTERNATIVASPAGADA A SOLICITUDPAGADA
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
  ELSE
    UPDATE "Booking"."Booking"
    SET "Button_options" = ''
    WHERE id = NEW."Booking_id";
  END IF;

  -- Current user
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
-- Acepta una alternativa y modifica la solicitud
BEGIN
  
  RESET ROLE;
  
  -- Update request with accepted option
  IF NEW."Accepted" THEN
    UPDATE "Booking"."Booking"
    SET "Building_id" = NEW."Building_id", 
      "Flat_type_id" = NEW."Flat_type_id", 
      "Place_type_id" = NEW."Place_type_id"
      "Status" = CASE
        WHEN "Status" = 'alternativas' THEN 'solicitud'
        WHEN "Status" = 'alternativaspagadas' THEN 'solicitudpagada'
        ELSE "Status"
      END
    WHERE id = NEW."Booking_id";
  END IF;

  -- Return
  RETURN NEW;

END;
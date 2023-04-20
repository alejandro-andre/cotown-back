BEGIN

  RESET ROLE;
    -- Exite una funcion 'Booking_caducar_solicitud' que cambiará el estado a 'caducadas' a todas las solicitudes caducadas 

    -- PENDIENTEPAGO a CADUCADA
	IF (NEW."Status" = 'caducada') THEN
		-- Envia email informando de la caducidad
		INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (NEW."Customer_id", 'caducada', NEW.id);
		-- Log
		INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, CONCAT('La solicitud ha caducado el día ', NEW."Expiry_date"));
	END IF;
  
  RETURN NEW;

END;

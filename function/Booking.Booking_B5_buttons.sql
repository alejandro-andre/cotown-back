-- Botones de reserva
DECLARE

   pending_payments INTEGER;

BEGIN

  --RESET ROLE;
  
  -- Boton descartar
  NEW."Button_discard" := '';
  IF NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas' OR NEW."Status" = 'pendientepago' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/descartada');
  END IF;
  IF NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/descartadapagada');
  END IF;

  -- Boton checkin
  NEW."Button_checkin" := '';
  IF NEW."Status" = 'checkin' THEN
     NEW."Button_checkin" := CONCAT('https://dev.cotown.ciber.es/api/v1/booking/', NEW.id, '/status/inhouse');
  END IF;

  -- Boton checkout
  NEW."Button_checkout" := '';
  -- Comprobamos que el usuario no tenga pagos pendientes.
  SELECT COUNT(*) INTO pending_payments FROM "Billing"."Payment"  WHERE "Payment"."Booking_id" = NEW.id AND "Payment"."Payment_date" IS NULL;
  IF NEW."Status" = 'checkout' AND pending_payments = 0 THEN    
     NEW."Button_checkout" := CONCAT('https://dev.cotown.ciber.es/booking/', NEW.id, '/status/devolvergarantia');
  END IF;

  -- Return
  RETURN NEW;

END;
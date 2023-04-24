-- Botones de reserva
BEGIN

  RESET ROLE;
  
  -- Boton descartar
  NEW."Button_discard" := '';
  IF NEW."Status" = 'solicitud' OR NEW."Status" = 'alternativas' OR NEW."Status" = 'pendientepago' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/booking/', NEW.id, '/status/descartada');
  END IF;
  IF NEW."Status" = 'solicitudpagada' OR NEW."Status" = 'alternativaspagada' THEN
     NEW."Button_discard" := CONCAT('https://dev.cotown.ciber.es/booking/', NEW.id, '/status/descartadapagada');
  END IF;

  -- Boton checkin
  NEW."Button_checkin" := '';
  IF NEW."Status" = 'checkin' THEN
     NEW."Button_checkin" := CONCAT('https://dev.cotown.ciber.es/booking/', NEW.id, '/status/inhouse');
  END IF;

  -- Boton checkout
  NEW."Button_checkout" := '';
  IF NEW."Status" = 'checkout' THEN
     NEW."Button_checkout" := CONCAT('https://dev.cotown.ciber.es/booking/', NEW.id, '/status/devolvergarantia');
  END IF;

  -- Return
  RETURN NEW;

END;
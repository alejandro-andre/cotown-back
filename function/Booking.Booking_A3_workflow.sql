-- Cancelacion de la solicitud confirmada
  DECLARE

  change VARCHAR = NULL;
  deposit_paid INTEGER;
  cacelation_fee_import INTEGER = 0;

BEGIN

  RESET ROLE;
  
  IF (NEW."Status" = 'cancelada') THEN
   
    -- Comprueba que el deposito este pagado
    SELECT COUNT(*) INTO deposit_paid 
    FROM "Billing"."Payment" 
    WHERE "Booking_id" = NEW."id" 
    AND "Payment_type" = 'deposito'
    AND "Payment_auth" IS NOT NULL 
	AND "Payment_date" IS NOT NULL;

    -- Si el deposito esta pagado genera el pago del la cancelación.
    IF(deposit_paid = 1) THEN
        cacelation_fee_import = 321;
        -- crea un registro de pago de la penalización (HE PUESTO 'servicos' porque PENALIZACION no existe.)
        INSERT INTO "Billing"."Payment"("Payment_method_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" ) VALUES ('1',NEW."id", cacelation_fee_import, CURRENT_DATE, 'Booking cancel', 'servicios');
        -- Log
        change := concat('Reserva cancelada. Recurso liberado: ' , NEW."Resource_id");   
    END IF;

     -- Desasocia el recurso de la reserva, actualiza la fecha de cancelacion y el cancelation fee (FALTA CALCULARLO)
    UPDATE "Booking"."Booking" SET  "Resource_id"=NULL, "Cancel_date"= CURRENT_DATE, "Cancelation_fee"=cacelation_fee_import WHERE id=NEW."id";
    

    -- Registra el cambio
    IF change IS NOT NULL THEN
        INSERT INTO "Booking"."Booking_log" ("Booking_id", "Log") VALUES (NEW.id, change);
    END IF;
  END IF;

  RETURN NEW;

END;

-- Fuerza la revisión de la documentación de la reserva
DECLARE

  curr_user VARCHAR;

BEGIN

  -- Documento sin reserva asociada (documentos de identidad): no hay nada que revisar
  IF NEW."Booking_id" IS NULL THEN
    RETURN NEW;
  END IF;

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE;

  -- Toca la reserva para que el workflow (Booking.Booking_B4_workflow) reevalúe la documentación.
  -- El criterio de 'documentación ok' vive allí, en un único sitio, y solo avanza desde
  -- 'confirmada', así que una reserva que ya ha avanzado (documentacionok, firmacontrato,
  -- contrato, checkin...) no retrocede al aprobar o añadir un documento.
  UPDATE "Booking"."Booking"
  SET "Status" = "Status"
  WHERE id = NEW."Booking_id"
    AND "Status" = 'confirmada';

  -- Fin
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;

-- Workflow
DECLARE

  status "Auxiliar"."Group_status";

BEGIN

  -- Status
  status := NEW."Status";

  -- Tentative
  IF status = 'grupobloqueado' THEN
    IF NEW."Confirmation_date" IS NOT NULL THEN
      status = 'grupoconfirmado';
    END IF;
  END IF;

  -- Confirmed
  IF status = 'grupoconfirmado' THEN
    IF NEW."Confirmation_date" IS NULL THEN
      status = 'grupobloqueado';
    ELSE
      IF NEW."Date_from" <= CURRENT_DATE THEN
	      status = 'inhouse';
      END IF;	
    END IF;
  END IF;

  -- In house
  IF status = 'inhouse' THEN
    IF NEW."Date_to" <= CURRENT_DATE THEN
       status = 'revision';
    END IF;	
  END IF;

  -- Revision
  IF status = 'revision' THEN
    IF NEW."Deposit_required" IS NOT NULL AND NEW."Date_deposit_required" IS NOT NULL THEN  
      status = 'devolvergarantia';
    END IF;	
  END IF;

  -- Return deposit
  IF status = 'devolvergarantia' THEN
    IF NEW."Deposit_returned" IS NOT NULL AND NEW."Date_deposit_returned" IS NOT NULL THEN  
      status = 'finalizada';
    END IF;	
  END IF;

  -- Update status
  IF status <> NEW."Status" OR (status IS NOT NULL AND NEW."Status" IS NULL) THEN
    NEW."Status" = status;
  END IF;

  -- Return record
  RETURN NEW;

END;
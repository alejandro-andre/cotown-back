-- Verifica los datos de la opcion
DECLARE

  curr_user VARCHAR;

BEGIN

  -- Check if has to send alternatives  
  curr_user := CURRENT_USER;
  RESET ROLE; 
	
  -- Tipología obligatoria
  IF NEW."Resource_type" <> 'piso' AND NEW."Place_type_id" IS NULL THEN
    RAISE exception '!!!Place type is mandatory!!!El tipo de plaza es obligatoria!!!'; 	
  END IF;

-- Current user
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW; 

END;
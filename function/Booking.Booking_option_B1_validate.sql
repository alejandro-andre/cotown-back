-- Verifica los datos de la opcion
BEGIN

 -- Tipología obligatoria
 IF NEW."Resource_type" <> 'piso' AND NEW."Place_type_id" IS NULL THEN
   RAISE exception '!!!Place type is mandatory!!!El tipo de plaza es obligatoria!!!'; 	
 END IF;
 RETURN NEW; 

END;
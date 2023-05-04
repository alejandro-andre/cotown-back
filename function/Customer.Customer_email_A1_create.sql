-- Creación de email
BEGIN

  EXECUTE 'NOTIFY email, ''' || NEW.id::text || '''';
  RETURN NEW;

END;
-- Verifica el proveedor
BEGIN

  -- No permite cambiar el email
  IF (OLD."Email" IS NOT NULL AND OLD."Email" <> NEW."Email") THEN
    RAISE EXCEPTION '!!!Email cannot be changed!!!No se puede cambiar el email!!!';
  END IF;

  -- Ok
  RETURN NEW;
  
END;
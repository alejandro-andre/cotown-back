-- Inicializa la solicitud
BEGIN

  NEW."Status" := 'solicitud';
  RETURN NEW;

END;
-- Inicializa datos
BEGIN
  NEW."Status" := 'solicitud';
  RETURN NEW;
END;
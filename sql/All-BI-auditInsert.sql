-- Actualiza los campos "created_"
BEGIN
  NEW."Created_by" := CURRENT_USER;
  NEW."Created_at" := NOW();
  RETURN NEW;
END;
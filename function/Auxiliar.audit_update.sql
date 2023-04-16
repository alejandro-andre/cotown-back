-- Actualiza los campos "updated_"
BEGIN

  RESET ROLE;
  NEW."Updated_by" := CURRENT_USER;
  NEW."Updated_at" := NOW();
  RETURN NEW;

END;
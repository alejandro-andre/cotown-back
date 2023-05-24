-- Audit
DECLARE

  user_name VARCHAR;
  record TEXT;
  changes TEXT;

BEGIN

  user_name := CURRENT_USER;
 
  IF TG_OP = 'INSERT' THEN
    NEW."Created_by" := user_name;
    NEW."Created_at" := NOW();
    record:= to_jsonb(NEW)::TEXT;
  END IF;

  IF TG_OP = 'UPDATE' THEN
    NEW."Updated_by" := user_name;
    NEW."Updated_at" := NOW(); 
    record = to_jsonb(OLD);
    WITH jsonb_diff AS (
      SELECT key, value AS value1, NULL::jsonb AS value2
      FROM jsonb_each(to_jsonb(OLD))
      WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(NEW))) AND jsonb_typeof(value) <> 'object'
      UNION ALL
      SELECT key, NULL::jsonb, value AS value2
      FROM jsonb_each(to_jsonb(NEW))
      WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(OLD))) AND jsonb_typeof(value) <> 'object'
    )
    SELECT jsonb_object_agg(key, COALESCE(value1, value2))
    INTO changes
    FROM jsonb_diff;
  END IF;
 
  IF TG_OP = 'DELETE' THEN
    record = to_jsonb(OLD);
  END IF;
  
  IF user_name <> 'modelsadmin' AND user_name <> 'postgres' THEN
    RESET ROLE;
    INSERT INTO "Admin"."Log" ("Table", "Action", "User", "When", "Record", "Changes")
    VALUES (TG_TABLE_NAME, TG_OP, user_name, NOW(), record, changes);
    EXECUTE 'SET ROLE "' || user_name || '"';
  END IF;
  
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  END IF;
  RETURN NEW;

END;
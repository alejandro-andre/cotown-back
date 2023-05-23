DECLARE

	username VARCHAR;
  record TEXT;
	changes TEXT;

BEGIN

  username := CURRENT_USER;
  RESET ROLE;
 
  IF TG_OP = 'INSERT' THEN
    NEW."Created_by" := username;
    NEW."Created_at" := NOW();
    record:= to_jsonb(NEW)::TEXT;
  END IF;

  IF TG_OP = 'UPDATE' THEN
    NEW."Updated_by" := username;
    NEW."Updated_at" := NOW(); 
    record = to_jsonb(OLD);
    WITH jsonb_diff AS (
      SELECT key, value AS value1, NULL::jsonb AS value2
      FROM jsonb_each(to_jsonb(OLD))
      WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(NEW)))
      UNION ALL
      SELECT key, NULL::jsonb, value AS value2
      FROM jsonb_each(to_jsonb(NEW))
      WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(OLD)))
    )
    SELECT jsonb_object_agg(key, COALESCE(value1, value2))
    INTO changes
    FROM jsonb_diff;
  END IF;
 
  IF TG_OP = 'DELETE' THEN
    record = to_jsonb(OLD);
  END IF;
  
  INSERT INTO "Admin"."Log" ("Table", "Action", "User", "When", "Record", "Changes")
  VALUES (TG_TABLE_NAME, TG_OP, username, NOW(), record, changes);
  
  RETURN NEW;

END;

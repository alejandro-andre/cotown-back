-- Audit
DECLARE

  curr_user VARCHAR;
  record TEXT;
  changes TEXT;

BEGIN

  -- Insert data
  IF TG_OP = 'INSERT' THEN
    NEW."Created_by" := curr_user;
    NEW."Created_at" := NOW();
    --?record:= to_jsonb(NEW)::TEXT;
  END IF;

  -- Update data
  IF TG_OP = 'UPDATE' THEN
    NEW."Updated_by" := curr_user;
    NEW."Updated_at" := NOW();
    --?record = to_jsonb(OLD);
    --?WITH jsonb_diff AS (
    --?  SELECT key, value AS value1, NULL::jsonb AS value2
    --?  FROM jsonb_each(to_jsonb(OLD))
    --?  WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(NEW))) AND jsonb_typeof(value) <> 'object'
    --?  UNION ALL
    --?  SELECT key, NULL::jsonb, value AS value2
    --?  FROM jsonb_each(to_jsonb(NEW))
    --?  WHERE NOT (key, value) IN (SELECT key, value FROM jsonb_each(to_jsonb(OLD))) AND jsonb_typeof(value) <> 'object'
    --?)
    --?SELECT jsonb_object_agg(key, COALESCE(value1, value2))
    --?INTO changes
    --?FROM jsonb_diff;
  END IF;

  -- Delete data
  --?IF TG_OP = 'DELETE' THEN
  --?  record = to_jsonb(OLD);
  --?END IF;
  --?IF curr_user <> 'modelsadmin' AND curr_user <> 'postgres' THEN
  --?  INSERT INTO "Admin"."Log" ("Table", "Action", "User", "When", "Record", "Changes")
  --?  VALUES (TG_TABLE_NAME, TG_OP, curr_user, NOW(), record, changes);
  --?END IF;

  -- Return
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  END IF;
  RETURN NEW;

END;
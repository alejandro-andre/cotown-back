BEGIN
NEW."Summary" := CASE WHEN LENGTH(NEW."Value") > 1000 THEN LEFT(NEW."Value", 997) || '...' ELSE NEW."Value" END;
NEW."Search":=COALESCE(NEW."Code"::text,'')||' '||COALESCE(NEW."Value"::text,'')||' '||COALESCE(NEW."Value_en"::text,''); RETURN NEW; 
END;
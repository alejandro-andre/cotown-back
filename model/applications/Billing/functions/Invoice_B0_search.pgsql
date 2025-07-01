DECLARE
  name VARCHAR;
  email VARCHAR;
BEGIN
  SELECT "Name", "Email" INTO name, email FROM "Customer"."Customer" WHERE id=NEW."Customer_id";
  NEW."Search":=COALESCE(NEW.id::text,'')||' '||COALESCE(name::text,'')||' '||COALESCE(email::text,'')||' '||COALESCE(NEW."Bill_type"::text,'')||' '||COALESCE(NEW."Code"::text,'')||' '||COALESCE(NEW."Concept"::text,'')||' '||COALESCE(NEW."Comments"::text,'')||' '||COALESCE(NEW."SAP_code"::text,''); 
  RETURN NEW; 
END;
DECLARE
  name VARCHAR;
  email VARCHAR;
BEGIN 
  SELECT "Name", "Email" INTO name, email FROM "Customer"."Customer" WHERE id=NEW."Customer_id";
  NEW."Search":=COALESCE(NEW.id::text,'')||' '||COALESCE(name::text,'')||' '||COALESCE(email::text,'')||' '||COALESCE(NEW."Payment_type"::text,'')||' '||COALESCE(NEW."Payment_order"::text,'')||' '||COALESCE(NEW."Payment_auth"::text,'')||' '||COALESCE(NEW."Concept"::text,'')||' '||COALESCE(NEW."Comments"::text,''); 
RETURN NEW; 
END;
DECLARE
  name VARCHAR;
  email VARCHAR;
BEGIN
  SELECT "Name", "Email" INTO name, email FROM "Customer"."Customer" WHERE id=NEW."Payer_id";
  NEW."Search":=COALESCE(NEW.id::text,'')||' '||COALESCE(name::text,'')||' '||COALESCE(email::text,'')||' '||COALESCE(NEW."Status"::text,'')||' '||COALESCE(NEW."Room_ids"::text,'')||' '||COALESCE(NEW."Comments"::text,'');  
  NEW."Customer":=name;  
  RETURN NEW; 
END;
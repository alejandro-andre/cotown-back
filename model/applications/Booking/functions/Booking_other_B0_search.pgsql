DECLARE
  name VARCHAR;
  email VARCHAR;
  code VARCHAR;
  data VARCHAR;
BEGIN
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE "id" = NEW."Resource_id";
  SELECT c."Name", "Email"
    INTO name, email
    FROM "Customer"."Customer" c
    WHERE c.id = NEW."Customer_id";
  NEW."Search":=COALESCE(NEW.id::text,'')||' '||COALESCE(code::text,'')||' '||COALESCE(name::text,'')||' '||COALESCE(email::text,'')||' '||COALESCE(NEW."Comments"::text,'')||' '||COALESCE(NEW."Contribution_comments"::text,''); 
  RETURN NEW; 
END;
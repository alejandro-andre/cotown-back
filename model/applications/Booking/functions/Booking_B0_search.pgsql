DECLARE
  name VARCHAR;
  email VARCHAR;
  code VARCHAR;
  data VARCHAR;
BEGIN
  SELECT "Code" INTO code FROM "Resource"."Resource" WHERE "id" = NEW."Resource_id";
  SELECT c."Name", "Email", c."Name"||'  /  '||c."Email"||'  /  '||COALESCE("Phones"::TEXT,'')||'  /  '||COALESCE(DATE_PART('YEAR', age(NOW(), "Birth_date"))::TEXT,'')||'  /  '||COALESCE(g."Name"::TEXT,'')||'  /  '||COALESCE(l."Name"::TEXT,'')||'  /  '||COALESCE(p."Name"::TEXT,'')
    INTO name, email, data
    FROM "Customer"."Customer" c
    LEFT JOIN "Geo"."Country" p ON p.id = c."Nationality_id"
    LEFT JOIN "Auxiliar"."Gender" g ON g.id = c."Gender_id"
    LEFT JOIN "Auxiliar"."Language" l ON l.id = c."Language_id"
    WHERE c.id = NEW."Customer_id";
  NEW."Customer":= name;
  NEW."Info":= data;
  NEW."Search":=COALESCE(NEW.id::text,'')||' '||COALESCE(code::text,'')||' '||COALESCE(name::text,'')||' '||COALESCE(email::text,'')||' '||COALESCE(NEW."Comments"::text,'');
  RETURN NEW; 
END;
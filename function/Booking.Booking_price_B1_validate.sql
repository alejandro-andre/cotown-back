-- Precios y descuentos
BEGIN

  -- Rent discount
  IF NEW."Rent_discount" IS NOT NULL THEN
    NEW."Rent_discount_pct" := NEW."Rent_discount" / NEW."Rent" * 100;
  ELSE
    IF NEW."Rent_discount_pct" IS NOT NULL THEN 
    	NEW."Rent_discount" := NEW."Rent" * NEW."Rent_discount_pct" / 100;
      NEW."Rent_discount_pct" := NEW."Rent_discount" / NEW."Rent" * 100;
    END IF;
  END IF;
 
  -- Services discount
  IF NEW."Services_discount" IS NOT NULL THEN
    NEW."Services_discount_pct" := NEW."Services_discount" / NEW."Services" * 100;
  ELSE
    IF NEW."Services_discount_pct" IS NOT NULL THEN 
    	NEW."Services_discount" := NEW."Services" * NEW."Services_discount_pct" / 100;
      NEW."Services_discount_pct" := NEW."Services_discount" / NEW."Services" * 100;
    END IF;
  END IF;
 
  -- Return record
  RETURN NEW;

END

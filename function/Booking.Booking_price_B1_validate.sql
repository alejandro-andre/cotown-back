-- Precios y descuentos
BEGIN

 -- Avoid recursive calls
 IF pg_trigger_depth() > 1 THEN
   RETURN NEW;
 END IF;

 -- Rent discount
 IF NEW."Rent_discount" IS NOT NULL THEN
   NEW."Rent_discount_pct" := (NEW."Rent_discount" * 100) / NEW."Rent";
 ELSE
   IF NEW."Rent_discount_pct" IS NOT NULL THEN 
   	NEW."Rent_discount" := NEW."Rent" * NEW."Rent_discount_pct" / 100;
     NEW."Rent_discount_pct" := (NEW."Rent_discount" * 100) / NEW."Rent";
   END IF;
 END IF;

 -- Services discount
 IF NEW."Services_discount" IS NOT NULL THEN
   NEW."Services_discount_pct" := (NEW."Services_discount" * 100) / NEW."Services";
 ELSE
   IF NEW."Services_discount_pct" IS NOT NULL THEN 
   	NEW."Services_discount" := NEW."Services" * NEW."Services_discount_pct" / 100;
     NEW."Services_discount_pct" := (NEW."Services_discount" * 100) / NEW."Services";
   END IF;
 END IF;

 -- Discount reason
 IF (NEW."Rent_discount" IS NOT NULL OR NEW."Services_discount" IS NOT NULL) AND NEW."Discount_type_id" IS NULL THEN
   RAISE exception '!!!Discount reason mandatory!!!Motivo del descuento obligatorio!!!';
 END IF;

 -- Apply to all
 IF NEW."Apply_to_all" THEN
	UPDATE "Booking"."Booking_price"
   SET 
     "Rent_discount"         = NEW."Rent_discount",
     "Services_discount"     = NEW."Services_discount",
     "Rent_discount_pct"     = NEW."Rent_discount_pct",
     "Services_discount_pct" = NEW."Services_discount_pct",
     "Discount_type_id"      = NEW."Discount_type_id"
   WHERE "Booking_id" = NEW."Booking_id" 
   AND id <> NEW.id;
   NEW."Apply_to_all" := FALSE;
 END IF;

 -- Return record
 RETURN NEW;

END;
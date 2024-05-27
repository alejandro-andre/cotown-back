-- Precios y descuentos
BEGIN

  -- Avoid recursive calls
  IF pg_trigger_depth() > 1 THEN
    RETURN NEW;
  END IF;

  -- Rent discount %
  IF COALESCE(NEW."Rent_discount", 0) = 0 AND COALESCE(NEW."Rent_discount_pct", 0) <> 0 THEN
    NEW."Rent_discount" := NEW."Rent" * NEW."Rent_discount_pct" / 100;
  END IF;
  IF COALESCE(NEW."Rent_discount", 0) <> 0 THEN
	  IF NEW."Rent" <> 0 THEN
      NEW."Rent_discount_pct" := (NEW."Rent_discount" * 100) / NEW."Rent";
    ELSE
      NEW."Rent_discount_pct" := NULL;
    END IF;
  END IF;

  -- Services discount
  IF COALESCE(NEW."Services_discount", 0) = 0 AND COALESCE(NEW."Services_discount_pct", 0) <> 0 THEN
    NEW."Services_discount" := NEW."Services" * NEW."Services_discount_pct" / 100;
  END IF;
  IF COALESCE(NEW."Services_discount", 0) <> 0 THEN
	  IF NEW."Services" <> 0 THEN
      NEW."Services_discount_pct" := (NEW."Services_discount" * 100) / NEW."Services";
    ELSE
      NEW."Services_discount_pct" := NULL;
    END IF;
  END IF;

  -- Discount reason
  IF (COALESCE(NEW."Rent_discount", 0) <> 0 OR COALESCE(NEW."Services_discount", 0) <> 0) AND NEW."Discount_type_id" IS NULL THEN
    RAISE EXCEPTION '% % % %', NEW."Rent_date", NEW."Booking_id", NEW."Rent_discount", NEW."Services_discount";
    RAISE exception '!!!Discount reason mandatory!!!Motivo del descuento obligatorio!!!';
  END IF;

  -- Totals
  NEW."Rent_total" = NEW."Rent" + COALESCE(NEW."Rent_discount", 0);
  NEW."Services_total" = NEW."Services" + COALESCE(NEW."Services_discount", 0);

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

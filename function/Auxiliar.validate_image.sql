-- Validate image size
BEGIN

  IF (NEW."Image").width > 1920 THEN
    RAISE EXCEPTION '!!!Image cannot be wider than 1920px.!!!La imagen no puede ser mas ancha de 1920px.!!!';
  END IF;
  IF (NEW."Image").height > 1920 THEN
    RAISE EXCEPTION '!!!Image cannot be higher than 1920px.!!!La imagen no puede ser mas alta de 1920px.!!!';
  END IF;

  RETURN NEW;

END;

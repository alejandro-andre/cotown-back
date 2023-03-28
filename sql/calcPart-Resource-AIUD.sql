-- Calcula las partes de un piso que supone una plaza o habitación
DECLARE 
    reg RECORD;
    num INTEGER;
	parts INTEGER;
	resource_id INTEGER;
	room_id INTEGER;
    res VARCHAR;
BEGIN
	IF pg_trigger_depth() = 1 THEN
	
		-- Parts in the flat
		SELECT COUNT("Flat_id") - COUNT("Room_id") / 2
		INTO parts
		FROM "Resource"."Resource"
		WHERE "Flat_id" = NEW."Flat_id";
	
		-- Get all places
		FOR reg IN
			SELECT id, "Code", "Room_id", "Description" 
			FROM "Resource"."Resource" 
			WHERE "Flat_id" = NEW."Flat_id"
			FOR UPDATE
		LOOP
			SELECT count(*)
			INTO num
			FROM "Resource"."Resource"
			WHERE "Room_id" = reg.id;
			IF num = 0 THEN
				UPDATE "Resource"."Resource" SET "Part" = CONCAT('1/', parts) WHERE id=reg.id;
			ELSE
				UPDATE "Resource"."Resource" SET "Part" = CONCAT('2/', parts) WHERE id=reg.id;
			END IF;
		END LOOP;

	END IF;

  	-- Return
	RETURN NEW;
END;

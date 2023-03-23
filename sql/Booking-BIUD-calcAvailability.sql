-- Almacena las reservas en tabla auxiliar
DECLARE
	building_id INTEGER;
	flat_type_id INTEGER;
	place_type_id INTEGER;

	code VARCHAR;
	reg RECORD;
	cur CURSOR FOR 
		SELECT *
		FROM "Resource"."Resource"
		WHERE "Code" LIKE CONCAT(code, '%')
		OR code LIKE CONCAT("Code", '%');

BEGIN
	-- Delete all records related to that booking
	DELETE FROM "Booking"."Booking_detail"
	WHERE "Booking_id" = NEW.id;

	-- Get resource code
	SELECT "Code" INTO code FROM "Resource"."Resource" WHERE id = NEW."Resource_id";

	-- Open cursor
	OPEN cur;

	-- Next record
	FETCH cur INTO reg;

	-- Loop thru all parents and children
	WHILE (FOUND) LOOP
	
		-- Insert booking
		INSERT INTO "Booking"."Booking_detail" (
			"Booking_id", "Status", "Date_from", "Date_to", "Lock",
			"Resource_id", "Building_id", "Resource_type", "Flat_type_id", "Place_type_id"
		)
		VALUES (
			NEW.id, NEW."Status", NEW."Date_from", NEW."Date_to", (CASE WHEN reg.id = NEW."Resource_id" THEN FALSE ELSE TRUE END),
			reg.id, reg."Building_id", reg."Resource_type", reg."Flat_type_id", reg."Place_type_id"
		);

		-- Next record
 	FETCH cur INTO reg;
	
	END LOOP;

	-- Close cursor
	CLOSE cur;
	
	-- Return
	RETURN NEW;
END;
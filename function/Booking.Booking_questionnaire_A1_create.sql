-- Add questions to questionnaire
-- AFTER INSERT
DECLARE

  curr_user VARCHAR;

BEGIN

  -- Superuser ROLE
  curr_user := CURRENT_USER;
  RESET ROLE; 

  -- Insert questions
  INSERT INTO "Booking"."Booking_answer" 
  ("Questionnaire_id", "Question_id")
  (
    SELECT NEW.id, bq.id  
    FROM "Booking"."Booking_question_group" bqg
    INNER JOIN "Booking"."Booking_question" bq ON bq."Group_id" = bqg.id
    WHERE bqg."Questionnaire_type" = NEW."Questionnaire_type"
  );

  -- End
  EXECUTE 'SET ROLE "' || curr_user || '"';
  RETURN NEW;

END;
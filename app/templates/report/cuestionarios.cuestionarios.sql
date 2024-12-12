SELECT bq2."Questionnaire_type", bq2."Completed", c."Name" AS "Customer", bq2."Booking_id", r."Code", bqg."Name" AS "Group", bq."Question", ba."Answer"
FROM "Booking"."Booking_answer" ba
INNER JOIN "Booking"."Booking_question" bq ON bq.id = ba."Question_id" 
INNER JOIN "Booking"."Booking_question_group" bqg ON bqg.id = bq."Group_id" 
INNER JOIN "Booking"."Booking_questionnaire" bq2 ON bq2.id = ba."Questionnaire_id" 
INNER JOIN "Booking"."Booking" b ON b.id = bq2."Booking_id" 
INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
WHERE bq2."Completed" IS NOT NULL
ORDER BY bq2."Questionnaire_type", ba."Questionnaire_id", bq."Order" 
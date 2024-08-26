-- Update IPC
BEGIN

UPDATE "Booking"."Booking_other"
SET 
  "Rent" = "Rent" * 1.1,
  "IPC_updated" = CURRENT_DATE
WHERE 
  EXTRACT(MONTH FROM "Date_from") = EXTRACT(MONTH FROM (CURRENT_DATE + INTERVAL '1 month'))
  AND AGE(CURRENT_DATE, "IPC_updated") >= INTERVAL '1 year';

END
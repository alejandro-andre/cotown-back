-- Update IPC
BEGIN
  UPDATE "Booking"."Booking_other"
  SET 
    "Rent" = "Rent" * (SELECT 1 + "Value_IPC"/ 100 FROM "Auxiliar"."Ipc" ORDER BY "Date_IPC" DESC LIMIT 1),
    "IPC_updated" = CURRENT_DATE
  WHERE 
    EXTRACT(MONTH FROM "Date_from") = "IPC_month"
  AND 
    EXTRACT(YEAR FROM "IPC_updated") < EXTRACT(YEAR FROM CURRENT_DATE);
END
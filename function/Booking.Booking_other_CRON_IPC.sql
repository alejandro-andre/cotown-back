-- Update IPC
BEGIN
  UPDATE "Booking"."Booking_other"
  SET 
    "Rent" = "Rent" * (SELECT 1 + "Value_IPC"/ 100 FROM "Auxiliar"."Ipc" ORDER BY "Date_IPC" DESC LIMIT 1),
    "IPC_updated" = CURRENT_DATE
  WHERE 
    EXTRACT(MONTH FROM "Date_from") = "IPC_month"
    AND ("IPC_updated" IS NULL OR AGE(CURRENT_DATE, "IPC_updated") >= INTERVAL '1 year');
END
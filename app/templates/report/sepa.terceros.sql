-- NetCash
SELECT 
  TRIM(c."Name") AS "Name", 
  REPLACE(COALESCE(c."IBAN", ''), ' ', '') AS "IBAN",
  LPAD(p."Booking_id"::text, 6, '0') AS "Ref_mandate",
  TO_CHAR(CURRENT_DATE, 'DD/MM/YYYY') AS "Date",
  'RCUR' AS "Sequence", 
  LPAD(p.id::text, 6, '0') AS "Ref_order",
  p."Amount",
  CASE p."Payment_type"
  	WHEN 'booking' THEN 'BOOKING FEE'
  	WHEN 'deposito' THEN 'DEPOSITO'
  	WHEN 'checkin' THEN 'CHECKIN'
  	ELSE 'RENTA ' || (ARRAY['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'])[EXTRACT(MONTH FROM p."Issued_date")] 
  END AS "Concept",
  (a."Name" || ' - ' || at."Name") AS "Agent"
FROM "Billing"."Payment" p
  LEFT JOIN "Customer"."Customer" c ON c.id = p."Customer_id"
  LEFT JOIN "Booking"."Booking" b ON b.id = p."Booking_id"
  LEFT JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
  LEFT JOIN "Provider"."Agent_type" at ON at.id = a."Agent_type_id"
WHERE p."Payment_method_id" = 2
  AND p."Payment_date" IS NULL 
  AND p."Booking_id" IS NOT NULL
  AND p."Pos" = 'delegado'
ORDER BY 1
;
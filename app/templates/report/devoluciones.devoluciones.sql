WITH 
"Invoices_due" AS (
  SELECT i."Booking_id", SUM(i."Total") AS "Amount"
  FROM "Billing"."Invoice" i 
    INNER JOIN "Billing"."Payment" p ON p.id = i."Payment_id" 
  WHERE NOT i."Rectified"
    AND i."Total" > 0
    AND p."Payment_method_id" <> 43 
    AND p."Payment_auth" IS NULL 
    AND i."Booking_id" IS NOT NULL
    AND i."Provider_id" <> 1
  GROUP BY 1
),
"Invoices_from_deposit" AS (
  SELECT i."Booking_id", SUM(i."Total") AS "Amount"
  FROM "Billing"."Invoice" i 
    INNER JOIN "Billing"."Payment" p ON p.id = i."Payment_id" 
  WHERE NOT i."Rectified"
    AND i."Total" > 0
    AND p."Payment_method_id" = 43 
    AND i."Booking_id" IS NOT NULL
    AND i."Provider_id" <> 1
  GROUP BY 1
),
"Invoices_due_cotown" AS (
  SELECT i."Booking_id", SUM(i."Total") AS "Amount"
  FROM "Billing"."Invoice" i 
    INNER JOIN "Billing"."Payment" p ON p.id = i."Payment_id" 
  WHERE NOT i."Rectified"
    AND i."Total" > 0
    AND p."Payment_method_id" <> 43 
    AND p."Payment_auth" IS NULL 
    AND i."Booking_id" IS NOT NULL
    AND i."Provider_id" = 1
  GROUP BY 1
),
"Invoices_from_deposit_cotown" AS (
  SELECT i."Booking_id", SUM(i."Total") AS "Amount"
  FROM "Billing"."Invoice" i 
    INNER JOIN "Billing"."Payment" p ON p.id = i."Payment_id" 
  WHERE NOT i."Rectified"
    AND i."Total" > 0
    AND p."Payment_method_id" = 43 
    AND i."Booking_id" IS NOT NULL
    AND i."Provider_id" = 1
  GROUP BY 1
)
SELECT 
  b.id,
  COALESCE(b."Check_out", b."Date_to") AS "Check_out",
  b."Deposit_actual",
  COALESCE(d."Amount", 0) AS "Amount_due",
  COALESCE(g."Amount", 0) AS "Amount_from_deposit",
  COALESCE(dc."Amount", 0) AS "Amount_due_cotown",
  COALESCE(gc."Amount", 0) AS "Amount_from_deposit_cotown",
  b."Damages",
  CASE 
    WHEN b."Status" = 'checkout' THEN 'Check-out'
    WHEN b."Status" = 'revision' THEN 'Revision'
    ELSE 'Devolucion fianza'
  END AS "Status",
  CASE 
    WHEN b."Destination_id" IS NOT NULL THEN 'CHA'   
  END AS "Substatus",
  c."Name",
  c."Email",
  c."Phones",
  r."Code",
  c."Bank_account", c."Swift", c."Bank_holder", c."Bank_name", c."Bank_address", c."Bank_city", co."Name" AS "Bank_country",
  CASE 
    WHEN co."Sepa" THEN 'SEPA'
    ELSE ''
  END AS "Sepa",
  p."Name" AS "Owner"
FROM "Booking"."Booking" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
  LEFT JOIN "Geo"."Country" co ON co."Code" = substring(c."Bank_account", 1, 2) 
  LEFT JOIN "Invoices_due" d ON d."Booking_id" = b.id
  LEFT JOIN "Invoices_from_deposit" g ON g."Booking_id" = b.id
  LEFT JOIN "Invoices_due_cotown" dc ON dc."Booking_id" = b.id
  LEFT JOIN "Invoices_from_deposit_cotown" gc ON gc."Booking_id" = b.id
WHERE b."Status" IN ('checkout', 'revision', 'devolvergarantia')
ORDER BY 2, 1 ASC
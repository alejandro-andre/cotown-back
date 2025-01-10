(
(
WITH
"Agent_bills" AS (
  SELECT 
    b.id,
    ab."Amount",
    ab."Date_from" AS "Bill_date_from", 
    ab."Date_to" AS "Bill_date_to",
    COUNT(b.id) OVER (PARTITION BY ab.id) AS "Booking_count",
    CASE 
      WHEN COUNT(b.id) OVER (PARTITION BY ab.id) > 0 THEN 
        ab."Amount" / COUNT(b.id) OVER (PARTITION BY ab.id)
      ELSE 0
    END AS "Cost"
  FROM "Provider"."Agent_bills" ab 
    LEFT JOIN "Booking"."Booking" b 
      ON b."Agent_id" = ab."Agent_id" 
     AND ab."Date_from" <= b."Confirmation_date" 
     AND ab."Date_to" >= b."Confirmation_date"
)
SELECT 
  a."Name" AS "Marketplace", 
  b."Confirmation_date",
  '' || b.id AS "id",
  a."Commision_percent" / 100 AS "Commision_percent",
  a."Commision_value", 
  at."Name" AS "Agent_type",
  COALESCE(b."Booking_fee_actual", 0) AS "Booking_fee",
  c."Name" AS "Customer", 
  substring(r."Code", 1, 6) AS "Building", 
  substring(r."Code", 8, 5) AS "Flat", 
  substring(r."Code", 14, 9) AS "Place", 
  rpt."Code" AS "Place_type", 
  b."Date_from", 
  b."Date_to",
  COALESCE(b."Commision", 0) AS "Direct_cost",
  COALESCE(pc."Cost", 0) AS "Prorrated_cost",
  pc."Amount",
  (SELECT SUM(bp."Rent_total")+SUM(bp."Services_total") AS "Rent" FROM "Booking"."Booking_price" bp WHERE bp."Booking_id" = b.id) AS "Rent",
  COALESCE(t."Value", 0) / 100 AS "Tax",
  r."Management_fee" / 100 AS "Management_fee"
FROM "Booking"."Booking" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id" 
  INNER JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
  INNER JOIN "Provider"."Agent_type" at ON AT.id = a."Agent_type_id" 
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
  LEFT JOIN "Agent_bills" pc ON pc.id = b.id
  LEFT JOIN "Building"."Building_type" bt ON bt.id = bu."Building_type_id" 
  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id" 
  WHERE b."Confirmation_date" >= %(fdesde)s AND b."Confirmation_date" < %(fhasta)s
)

UNION 

(
WITH
"Agent_bills" AS (
  SELECT 
    b.id,
    ab."Amount",
    ab."Date_from" AS "Bill_date_from", 
    ab."Date_to" AS "Bill_date_to",
    COUNT(b.id) OVER (PARTITION BY ab.id) AS "Booking_count",
    CASE 
      WHEN COUNT(b.id) OVER (PARTITION BY ab.id) > 0 THEN 
        ab."Amount" / COUNT(b.id) OVER (PARTITION BY ab.id)
      ELSE 0
    END AS "Cost"
  FROM "Provider"."Agent_bills" ab 
    LEFT JOIN "Booking"."Booking_group" b 
      ON b."Agent_id" = ab."Agent_id" 
     AND ab."Date_from" <= b."Confirmation_date" 
     AND ab."Date_to" >= b."Confirmation_date"
)
SELECT 
  a."Name" AS "Marketplace", 
  b."Confirmation_date",
  'G' ||b.id AS "id",
  a."Commision_percent" / 100 AS "Commision_percent",
  a."Commision_value", 
  at."Name" AS "Agent_type",
  0 AS "Booking_fee",
  c."Name" AS "Customer", 
  substring(r."Code", 1, 6) AS "Building", 
  '...' AS "Flat", 
  '...' AS "Place", 
  '...' AS "Place_type", 
  b."Date_from", 
  b."Date_to", 
  COALESCE(b."Commision", 0) AS "Direct_cost",
  COALESCE(pc."Cost", 0) AS "Prorrated_cost",
  pc."Amount",
  (SELECT SUM(bp."Rent")+SUM(bp."Services") AS "Rent" FROM "Booking"."Booking_group_price" bp WHERE bp."Booking_id" = b.id) AS "Rent",
  CASE
    WHEN t."Value" IS NOT NULL THEN t."Value" / 100
    WHEN b."Tax" THEN 0
    ELSE 0.21
  END AS "Tax",
  r."Management_fee" / 100 AS "Management_fee"
FROM "Booking"."Booking_group" b
  INNER JOIN "Customer"."Customer" c ON c.id = b."Payer_id" 
  INNER JOIN "Building"."Building" r ON r.id = b."Building_id" 
  INNER JOIN "Provider"."Agent" a ON a.id = b."Agent_id"
  INNER JOIN "Provider"."Agent_type" at ON AT.id = a."Agent_type_id" 
  LEFT JOIN "Agent_bills" pc ON pc.id = b.id
  LEFT JOIN "Building"."Building_type" bt ON bt.id = r."Building_type_id" 
  LEFT JOIN "Billing"."Tax" t ON t.id = bt."Tax_id" 
  WHERE b."Confirmation_date" >= %(fdesde)s AND b."Confirmation_date" < %(fhasta)s
)

ORDER BY 1, 2, 3
);
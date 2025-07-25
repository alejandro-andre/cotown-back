WITH 
params AS (
  SELECT 
    (DATE_TRUNC('month', CURRENT_DATE) + (n + 1 || ' month')::interval - INTERVAL '1 day')::date AS month_end,
    TO_CHAR(DATE_TRUNC('month', CURRENT_DATE) + (n || ' month')::interval, 'YYYY_MM') AS label
  FROM generate_series(0, 5) AS n
),
bookings AS (
  SELECT 
    b.id,
    etlb.labels[array_position(etb.values, b."Status"::text)] AS "Status",
    CASE WHEN b."Deposit_locked" THEN 'Si' ELSE 'No' END as "Deposit_locked",
    c."Name" AS "Customer",
    r."Code" AS "Resource",
    p."Name" AS "Owner",
    DATE_TRUNC('month', CURRENT_DATE)::DATE AS "Today",
    COALESCE(b."Check_out", b."Date_to") AS "Date_to",
    CASE 
      WHEN COALESCE(b."Check_out", b."Date_to") < DATE_TRUNC('month', CURRENT_DATE)::DATE THEN (DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month') - INTERVAL '1 day')::DATE
      WHEN EXTRACT(DAY FROM COALESCE(b."Check_out", b."Date_to")) < 20 THEN (DATE_TRUNC('month', COALESCE(b."Check_out", b."Date_to") + INTERVAL '1 month') - INTERVAL '1 day')::DATE
      ELSE (DATE_TRUNC('month', COALESCE(b."Check_out", b."Date_to") + INTERVAL '2 months') - INTERVAL '1 day')::DATE
    END AS "Return_date",
    COALESCE(b."Deposit_required", b."Deposit_actual") AS "Deposit"
  FROM "Booking"."Booking" b
    INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
    INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
    INNER JOIN "Models"."EnumType" etb ON etb.id = 7
    INNER JOIN "Models"."EnumTypeLabel" etlb ON etlb.container = etb.id AND etlb.locale = 'es_ES'
  WHERE b."Destination_id" IS NULL
    AND COALESCE(b."Deposit_required", b."Deposit_actual") > 1
    AND b."Date_to" < (CURRENT_DATE + INTERVAL '5 months')
    AND b."Status" IN ('firmacontrato', 'checkin', 'contrato', 'inhouse', 'checkout', 'revision', 'devolvergarantia')
)
SELECT 
  b.id,
  b."Status",
  b."Deposit_locked",
  b."Customer",
  b."Resource",
  b."Owner",
  b."Today",
  b."Date_to",
  b."Return_date",
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE, 'YYYY_MM')) 
       THEN b."Deposit" END AS month_0,
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE + INTERVAL '1 month', 'YYYY_MM')) 
       THEN b."Deposit" END AS month_1,
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE + INTERVAL '2 month', 'YYYY_MM')) 
       THEN b."Deposit" END AS month_2,
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE + INTERVAL '3 month', 'YYYY_MM')) 
       THEN b."Deposit" END AS month_3,
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE + INTERVAL '4 month', 'YYYY_MM')) 
       THEN b."Deposit" END AS month_4,
  CASE WHEN b."Return_date" = (SELECT month_end FROM params WHERE label = TO_CHAR(CURRENT_DATE + INTERVAL '5 month', 'YYYY_MM')) 
       THEN b."Deposit" END AS month_5
FROM bookings b
ORDER BY "Date_to";
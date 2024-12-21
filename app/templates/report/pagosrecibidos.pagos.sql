WITH RankedInvoices AS (
  SELECT 
    p.id AS "Payment_id", 
    p."Amount", 
    COALESCE(p."Amount_payed", p."Amount") AS "Amount_payed",
    p."Booking_id", 
    p."Booking_group_id", 
    p."Comments", 
    p."Concept",
    p."Issued_date", 
    p."Payment_auth", 
    p."Payment_date", 
    p."Payment_order", 
    p."Pos",
    c."Name" AS "Customer_name", 
    c."Email" AS "Customer_email",
    r."Code" AS "Resource",
    pm."Name" AS "Payment_method",
    i."Code" AS "Invoice_code",
    i."Issued_date" AS "Invoice_date",
    i."Concept" AS "Invoice_concept",
    i."Total",
    ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY i."Issued_date" ASC) AS "Invoice_rank"
  FROM "Billing"."Payment" p
    LEFT JOIN "Booking"."Booking" b ON b.id = p."Booking_id"
    LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    INNER JOIN "Billing"."Payment_method" pm ON pm.id = p."Payment_method_id"
    INNER JOIN "Customer"."Customer" c ON c.id = p."Customer_id"
    INNER JOIN "Billing"."Invoice" i ON i."Payment_id" = p.id
  WHERE p."Payment_date" BETWEEN %(fdesde)s::date AND %(fhasta)s::date
)
SELECT 
  ri."Payment_id", 
  MAX(CASE WHEN "Invoice_rank" = 1 THEN ri."Invoice_code" ELSE NULL END) AS "Invoice_code_1",
  MAX(CASE WHEN "Invoice_rank" = 1 THEN ri."Invoice_concept" ELSE NULL END) AS "Invoice_concept_1",
  MAX(CASE WHEN "Invoice_rank" = 1 THEN ri."Total" ELSE NULL END) AS "Invoice_total_1",
  MAX(CASE WHEN "Invoice_rank" = 2 THEN ri."Invoice_code" ELSE NULL END) AS "Invoice_code_2",
  MAX(CASE WHEN "Invoice_rank" = 2 THEN ri."Invoice_concept" ELSE NULL END) AS "Invoice_concept_2",
  MAX(CASE WHEN "Invoice_rank" = 2 THEN ri."Total" ELSE NULL END) AS "Invoice_total_2",
  MAX(CASE WHEN "Invoice_rank" = 3 THEN ri."Invoice_code" ELSE NULL END) AS "Invoice_code_3",
  MAX(CASE WHEN "Invoice_rank" = 3 THEN ri."Invoice_concept" ELSE NULL END) AS "Invoice_concept_3",
  MAX(CASE WHEN "Invoice_rank" = 3 THEN ri."Total" ELSE NULL END) AS "Invoice_total_3",
  MAX(CASE WHEN "Invoice_rank" = 4 THEN ri."Invoice_code" ELSE NULL END) AS "Invoice_code_4",
  MAX(CASE WHEN "Invoice_rank" = 4 THEN ri."Invoice_concept" ELSE NULL END) AS "Invoice_concept_4",
  MAX(CASE WHEN "Invoice_rank" = 4 THEN ri."Total" ELSE NULL END) AS "Invoice_total_4",
  ri."Amount", 
  ri."Amount_payed", 
  ri."Booking_id", 
  ri."Booking_group_id", 
  ri."Resource",
  ri."Comments", 
  ri."Concept",
  ri."Issued_date", 
  ri."Payment_auth", 
  ri."Payment_date", 
  ri."Payment_order", 
  ri."Pos",
  ri."Customer_name", 
  ri."Customer_email",
  ri."Payment_method"
FROM RankedInvoices ri
WHERE "Invoice_rank" <= 4
GROUP BY 
  ri."Payment_id", 
  ri."Amount", 
  ri."Amount_payed", 
  ri."Booking_id", 
  ri."Booking_group_id", 
  ri."Resource", 
  ri."Comments", 
  ri."Concept", 
  ri."Issued_date", 
  ri."Payment_auth", 
  ri."Payment_date", 
  ri."Payment_order", 
  ri."Pos",
  ri."Customer_name", 
  ri."Customer_email", 
  ri."Payment_method"
ORDER BY ri."Issued_date";
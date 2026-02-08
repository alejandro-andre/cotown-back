SELECT
  p.id,
  p."Issued_date",
  p."Concept", 
  p."Payment_auth", 
  p."Payment_date", 
  p."Amount",
  p."Comments",
  pm."Name" AS "Payment_method",
  c."Name" AS "Customer",
  b.id AS "Booking_id", 
  b."Date_from", b."Date_to",
  r."Code" AS "Resource",
  bu."Code" AS "Building",
  STRING_AGG(i."Code", ', ') AS "Invoices",
  SUM(i."Total") AS "Invoice_total",
  p."Warning_1", p."Warning_2", p."Warning_3"
FROM "Billing"."Payment" p
  INNER JOIN "Billing"."Payment_method" pm ON pm.id = p."Payment_method_id"
  INNER JOIN "Billing"."Invoice" i ON i."Payment_id" = p.id
  INNER JOIN "Booking"."Booking" b ON b.id = p."Booking_id"
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
WHERE p."Amount" > 0 
  AND (p."Payment_date" IS NULL OR p."Payment_auth" IS NULL)
  AND pm."Name" NOT LIKE '%%garantía%%'
  AND pm."Name" NOT LIKE '%%Rectificativa%%'
GROUP BY
  p.id,
  p."Issued_date",
  p."Concept", 
  p."Payment_auth", 
  p."Payment_date", 
  p."Amount",
  p."Comments",
  c."Name",
  pm."Name",
  b.id, 
  b."Date_from", b."Date_to",
  r."Code",
  bu."Code"
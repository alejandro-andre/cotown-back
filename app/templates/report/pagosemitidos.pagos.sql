SELECT 
  il."Concept" AS "Line_concept", il."Comments" AS "Line_comments", il."Amount", 
  pd."Name" AS "Product_name",
  i."Issued_date", i."Code", i."Concept", i."Comments", 
  pr."Name" AS "Provider_name",
  c."Name" AS "Customer_name", c."Email" AS "Customer_email",
  p."Amount_payed", p."Payment_type", p."Payment_date", p."Payment_auth", p."Payment_order", p."Comments" AS "Payment_comments",
  b.id AS "Booking_id", b."Date_from" AS "Booking_date_from", b."Date_to" AS "Booking_date_to",
  r."Resource_type", r."Code" AS "Resource", r."Address", 
  rft."Code" AS "Flat_type_code", rft."Name" AS "Flat_type_name",
  rpt."Code" AS "Place_type_code", rpt."Name" AS "Place_type_name",
  bg.id AS "Booking_group_id", bg."Date_from" AS "Booking_group_date_from", bg."Date_to" AS "Booking_group_date_to",
  bo.id AS "Booking_other_id", bo."Date_from" AS "Booking_other_date_from", bo."Date_to" AS "Booking_other_date_to",
  bu."Code" AS "Building",
  p."Warning_1", p."Warning_2", p."Warning_3"
FROM "Billing"."Invoice_line" il
  INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id"
  INNER JOIN "Billing"."Product" pd ON pd.id = il."Product_id"
  INNER JOIN "Provider"."Provider" pr ON pr.id = i."Provider_id"
  INNER JOIN "Customer"."Customer" c ON c.id = i."Customer_id" 
  LEFT JOIN "Billing"."Payment" p ON p.id = i."Payment_id" 
  LEFT JOIN "Billing"."Payment_method" pm ON pm.id = p."Payment_method_id"
  LEFT JOIN "Booking"."Booking" b ON b.id = i."Booking_id" 
  LEFT JOIN "Booking"."Booking_group" bg ON bg.id = i."Booking_group_id" 
  LEFT JOIN "Booking"."Booking_other" bo ON bo.id = i."Booking_other_id"
  LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
  LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
  LEFT JOIN "Building"."Building" bu ON bu.id = bg."Building_id" 
WHERE i."Issued"
  AND i."Issued_date" >= %(fdesde)s::date 
  AND i."Issued_date" < %(fhasta)s::date
  AND i."Provider_id" BETWEEN %(pdesde)s AND %(phasta)s
ORDER BY i."Issued_date", i."Provider_id", i."Code"
;
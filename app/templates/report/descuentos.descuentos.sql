SELECT 
  b.id,
  r."Code",
  bp."Rent_date", 
  bp."Rent", COALESCE(bp."Rent_discount", 0) AS "Rent_discount", bp."Rent_total",
  bdt."Name" AS "Discount_type",
  pr."Name" AS "Promotion",
  bp."Comments",
  p."Name" AS "Owner",
  l."Name" AS "City",
  bu."Code" AS "Building",
  rft."Code" AS "Flat_type",
  rpt."Code" AS "Place_type"
FROM "Booking"."Booking_price" bp
  INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id"
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  INNER JOIN "Geo"."District" d ON d.id = bu."District_id"
  INNER JOIN "Geo"."Location" l ON l.id = d."Location_id"
  INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
  INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
  LEFT JOIN "Booking"."Booking_discount_type" bdt ON bdt.id = bp."Discount_type_id"
  LEFT JOIN "Billing"."Promotion" pr ON pr.id = b."Promotion_id"
WHERE bp."Rent_total" <> bp."Rent"
ORDER BY 1, 3
;
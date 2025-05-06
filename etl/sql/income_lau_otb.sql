WITH
"Dates" AS (
  SELECT generate_series(DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month'), '2030-01-01'::date - interval '1 day', interval '1 month')::date AS "Date"
)
SELECT 
  'LOX' || b.id::TEXT || '.' || d."Date" AS "id",
  b.id AS "doc_id",
  '-' AS "doc_type",
  'L' || b.id::text AS "booking",
  d."Date" AS "date",
  p."Document" AS "provider",
  b."Customer_id" AS "customer",
  r."Code" AS "resource",
  CASE 
	  WHEN b."Booking_type" = 'lau' THEN
      CASE
        WHEN b."Date_estimated" IS NULL AND b."Date_to" IS NULL THEN 'LTNC'
        WHEN b."Date_estimated" IS NOT NULL AND b."Date_to" IS NULL THEN 'LTC'
        ELSE 'FTC'
      END
	  WHEN b."Booking_type" = 'parking' THEN 'PARKING'
	  WHEN b."Booking_type" = 'coworking' THEN 'COWORKING'
	  ELSE 'RETAIL'
  END AS "stay_length",
  pr."Name_en" AS "product",
  (COALESCE(b."Rent", 0) + COALESCE(b."Extras", 0)) / (1 + (t."Value" / 100)) AS "amount",
  0 AS "rate",
  NULL AS "price",
  CASE
    WHEN b."Unlawful" THEN 'Tentative'
    ELSE 'OTB'
  END AS "data_type",
  '' AS "discount_type"
FROM "Booking"."Booking_other" b
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
  INNER JOIN "Building"."Building" bu on bu.id = r."Building_id" 
  INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id" 
  INNER JOIN "Billing"."Product" pr ON pr.id = b."Product_id"
  INNER JOIN "Billing"."Product_type" pt ON pt.id = pr."Product_type_id" 
  INNER JOIN "Billing"."Tax" t ON t.id = pr."Tax_id" 
  INNER JOIN "Dates" d ON d."Date" BETWEEN b."Date_from" AND COALESCE(b."Date_estimated", b."Date_to", '2030-01-01'::date)
ORDER BY 2
;
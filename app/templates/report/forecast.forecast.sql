-- Forecast
WITH months AS (
  SELECT generate_series(
    %(fdesde)s::date, %(fhasta)s::date - '1 day'::interval, '1 month'::interval
  ) AS month_date
)
SELECT
  r."Code", m.month_date::date AS "Date_price", rf."Occupancy"/100 AS "Occupancy", 
  rf."Rent_short"/100 AS "Rent_short", rf."Rent_medium"/100 AS "Rent_medium", rf."Rent_long"/100 AS "Rent_long", rf."Discount"/100 AS "Discount",
  rf."Services", rf."Final_cleaning", rf."Booking_fee", rf."Reinvoices"    
FROM "Resource"."Resource" r 
  CROSS JOIN months m  
  LEFT JOIN "Resource"."Resource_forecast" rf ON rf."Resource_id" = r.id AND rf."Date_price" = m.month_date
WHERE r."Resource_type" = 'piso'
ORDER BY 1, 2
;
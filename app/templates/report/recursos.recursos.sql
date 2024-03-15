WITH
extras AS (
	SELECT 
		r.id, 
		string_agg(rat."Code", ',') AS "extras",
		exp(sum(ln(1 + coalesce(rat."Increment", 0) / 100))) AS "increment"
	FROM "Resource"."Resource" r
	LEFT JOIN "Resource"."Resource_amenity" ra on ra."Resource_id" = r.id
	LEFT JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id" 
	GROUP BY 1
),
locks AS (
	SELECT 
		ra."Resource_id" AS id,
		string_agg(rs."Name", ',') AS "type",
		string_agg(to_char(ra."Date_from", 'YYYY-MM-DD'), ',') AS "from",
		string_agg(to_char(ra."Date_to", 'YYYY-MM-DD'), ',') AS "to"
	FROM "Resource"."Resource_availability" ra 
	LEFT JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id" 
	GROUP BY 1
)
SELECT 
	o."Name" AS "Owner.Name", s."Name" AS "Service.Name",
	ex.extras AS "extras",
	(ex.increment - 1) * 100 AS "increment",
	lck."type" "unavailable",
	lck."from" AS "from",
	lck."to" AS  "to",
	r."Code", r."SAP_code", 
	r."Street", r."Address", 
	rft."Code" AS "Flat_type.Code", 
	rfs."Code" AS "Flat_subtype.Code", 
	rpt."Code" AS "Place_type.Code",
	r."Billing_type", r."Sale_type",
	pr."Code" AS "Pricing_rate.Code",
	r."Description", r."Description_en", 
	r."Area", r."Baths", r."Places", r."Orientation", r."Wifi_ssid", r."Wifi_key", r."Gate_mac", r."Gate_phone", r."Notes"
FROM "Resource"."Resource" r
INNER JOIN "Provider"."Provider" o ON o.id = r."Owner_id" 
INNER JOIN "Provider"."Provider" s ON s.id = r."Service_id"
INNER JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id" 
INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
LEFT JOIN "Resource"."Resource_flat_subtype" rfs ON rfs.id = r."Flat_subtype_id" 
LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
LEFT JOIN "extras" ex ON ex.id = r.id
LEFT JOIN "locks" lck ON lck.id = r.id
ORDER BY r."Code"

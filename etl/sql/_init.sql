-- Drop Core tables
DROP TABLE IF EXISTS gold.date CASCADE;
DROP TABLE IF EXISTS gold.flat_type CASCADE;
DROP TABLE IF EXISTS gold.place_type CASCADE;
DROP TABLE IF EXISTS gold.product CASCADE;
DROP TABLE IF EXISTS gold.owner CASCADE;
DROP TABLE IF EXISTS gold.location CASCADE;
DROP TABLE IF EXISTS gold.resource_history CASCADE;
DROP TABLE IF EXISTS gold.resource CASCADE;
DROP TABLE IF EXISTS gold.income CASCADE;
DROP TABLE IF EXISTS gold.occupancy CASCADE;
DROP TABLE IF EXISTS gold.beds CASCADE;
DROP TABLE IF EXISTS gold.booking CASCADE;
DROP TABLE IF EXISTS gold.marketplace CASCADE;

-- Drop SAP tables
DROP TABLE IF EXISTS gold.gl CASCADE;
DROP TABLE IF EXISTS gold.mapping CASCADE;


-- -------------------------------------
-- Dates
-- -------------------------------------

-- Create dates table
CREATE TABLE gold.date (
  "date" date NOT NULL,
  "day" int2 NOT NULL,
  "dow" int2 NOT NULL,
  "downame" varchar NOT NULL,
  "week" int2 NOT NULL,
  "month" int2 NOT NULL,
  "monthname" varchar NOT NULL,
  "monthshort" varchar NOT NULL,
  "year" int2 NOT NULL,
  "quarter" int2 NOT NULL,
  "quartername" varchar NOT NULL,
  "semester" int2 NOT NULL,
  "semestername" varchar NOT NULL,
  "yearsemester" varchar NOT NULL,
  "yearquarter" varchar NOT NULL,
  "yearmonth" varchar NOT NULL,
  "yearweek" varchar NOT NULL,
CONSTRAINT date_pk PRIMARY KEY ("date")
);

-- Insert dates
INSERT INTO gold."date" (
  "date", "day", "dow", "downame", "week", "month", "monthname", "monthshort", "year", "quarter", "quartername", 
  "semester", "semestername", "yearsemester", "yearquarter", "yearmonth", "yearweek"
)
SELECT
  d::DATE AS "date",
  EXTRACT(DAY FROM d) AS "day",
  EXTRACT(ISODOW FROM d) AS "dow",
  (ARRAY['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])[EXTRACT(ISODOW FROM d)],
  EXTRACT(WEEK FROM d) AS "week",
  EXTRACT(MONTH FROM d) AS "month",
  (ARRAY['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])[EXTRACT(MONTH FROM d)] AS "monthname",
  (ARRAY['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])[EXTRACT(MONTH FROM d)] AS "monthshort",
  EXTRACT(YEAR FROM d) AS "year",
  EXTRACT(QUARTER FROM d) AS "quarter",
  'Q' || EXTRACT(QUARTER FROM d)::TEXT AS "quartername",
  CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 1 ELSE 2 END AS "semester",
  CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 'S1' ELSE 'S2' END AS "semestername",
  EXTRACT(YEAR FROM d)::TEXT || '-' || CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 'S1' ELSE 'S2' END AS "yearsemester",
  EXTRACT(YEAR FROM d)::TEXT || '-Q' || EXTRACT(QUARTER FROM d)::TEXT AS "yearquarter",
  TO_CHAR(d, 'YYYY-MM') AS "yearmonth",
  TO_CHAR(d, 'YYYY-WW') AS "yearweek"
FROM
  generate_series('2024-01-01'::DATE, '2029-12-31'::DATE, '1 day') AS d;


-- -------------------------------------
-- Dimensions
-- -------------------------------------

-- Create owners table
CREATE TABLE gold.owner (
  "id" varchar NOT NULL,
  "type" varchar NOT NULL,
  "name" varchar NOT NULL,
  "order" int8 NOT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT owner_pk PRIMARY KEY ("id")
);

-- Create product table
CREATE TABLE gold.product (
  "id" varchar NOT NULL,
  "type" varchar NOT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT product_pk PRIMARY KEY ("id")
);

-- Create locations table
CREATE TABLE gold.location (
  "id" varchar NOT NULL,
  "province" varchar NOT NULL,
  "country" varchar NOT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT location_pk PRIMARY KEY ("id")
);

-- Create flat type table
CREATE TABLE gold.flat_type (
  "id" varchar NOT NULL,
  "name" varchar NOT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT flat_type_pk PRIMARY KEY ("id")
);

-- Create place type table
CREATE TABLE gold.place_type (
  "id" varchar NOT NULL,
  "group" varchar NOT NULL,
  "name" varchar NOT NULL,
  "order" int4 NOT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT place_type_pk PRIMARY KEY ("id")
);

-- Create resources table
CREATE TABLE gold.resource (
  "id" varchar NOT NULL,
  "type" varchar NOT NULL,
  "owner" varchar NOT NULL,
  "location" varchar NOT NULL,
  "start_date" date DEFAULT NULL,
  "estabilised_date" date DEFAULT NULL, 
  "building" varchar NOT NULL,
  "building_name" varchar NOT NULL,
  "segment" varchar NOT NULL,
  "flat" varchar DEFAULT NULL,
  "flat_type" varchar DEFAULT NULL,
  "place_type" varchar DEFAULT NULL,
  "billing_type" varchar DEFAULT NULL,
  "area" numeric DEFAULT NULL,
  "rooms" numeric DEFAULT NULL,
  "beds" numeric DEFAULT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT resource_pk PRIMARY KEY ("id"),
CONSTRAINT resource_owner_fk FOREIGN KEY ("owner") REFERENCES gold.owner("id"),
CONSTRAINT resource_location_fk FOREIGN KEY ("location") REFERENCES gold.location("id")
);


-- -------------------------------------
-- Facts
-- -------------------------------------

-- Create resource history table
CREATE TABLE gold.resource_history (
  "id" varchar NOT NULL,
  "date" date NOT NULL,

  "area"  numeric NOT NULL,               -- Area m2
  "units" numeric NOT NULL,               -- Units (flats...)
  "rooms" numeric NOT NULL,               -- Rooms
  "beds" numeric NOT NULL,                -- Beds
  "data_type" varchar NOT NULL,           -- Real, OTB, Forecast...
  "resource" varchar NOT NULL,            -- Dimension resource
  "status" varchar NOT NULL,              -- COSHARING, LTC, LTNC, FTC, PRECAPEX, CAPEX, RETAIL, OTHER...
  "val_current" numeric DEFAULT NULL,     -- Current status valuation
  "val_residential" numeric DEFAULT NULL, -- Residential valuation
  "val_cosharing" numeric DEFAULT NULL,   -- Cosharing valuation
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT resource_history_pk PRIMARY KEY ("id"),
CONSTRAINT resource_history_resource_fk FOREIGN KEY ("resource") REFERENCES gold.resource("id")
);

-- Create beds table
CREATE TABLE gold.beds (
  "id" varchar NOT NULL,
  "date" date NOT NULL,

  "available" int NOT NULL,
  "beds" int NOT NULL,                  -- Converted beds
  "beds_c" numeric NOT NULL,            -- Consolidated beds
  "beds_cnv" numeric NOT NULL,          -- Convertible beds
  "beds_pot" numeric NOT NULL,          -- Potential beds
  "beds_cap" numeric NOT NULL,          -- Capex beds
  "beds_pre" numeric NOT NULL,          -- Pre capex beds
  "data_type" varchar NOT NULL,         -- Real, OTB, Forecast...
  "resource" varchar NOT NULL,          -- Dimension resource
  "convertible" varchar DEFAULT NULL,
  "val_current" numeric DEFAULT NULL,
  "val_residential" numeric DEFAULT NULL,
  "val_cosharing" numeric DEFAULT NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT beds_pk PRIMARY KEY ("id"),
CONSTRAINT beds_resource_fk FOREIGN KEY ("resource") REFERENCES gold.resource("id")
);

-- Create occupancy table
CREATE TABLE gold.occupancy (
  "id" varchar NOT NULL,
  "date" date NOT NULL,

  "booking" varchar DEFAULT NULL,
  "data_type" varchar NOT NULL,         -- Real, OTB, Forecast...
  "occupied" numeric NOT NULL,
  "occupied_t" numeric NOT NULL,
  "resource" varchar NOT NULL,          -- Dimension resource
  "sold" numeric NOT NULL,
  "sold_t" numeric NOT NULL,
  "stay_length" varchar NULL,           -- LONG, MEDIUM, SHORT, GROUP
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT occupancy_pk PRIMARY KEY ("id"),
CONSTRAINT occupancy_resource_fk FOREIGN KEY ("resource") REFERENCES gold.resource("id")
);

-- Create income table
CREATE TABLE gold.income (
  "id" varchar NOT NULL,
  "date" date NOT NULL,

  "amount" numeric NOT NULL,
  "booking" varchar DEFAULT NULL,
  "customer" int8 DEFAULT NULL,         -- Dimension resource
  "data_type" varchar NOT NULL,         -- Real, OTB, Forecast...
  "discount_type" varchar NULL,
  "doc_id" varchar NOT NULL,
  "doc_type" varchar NOT NULL,
  --"income_type" varchar NOT NULL,       -- B2B, B2C, ...
  "product" varchar NOT NULL,
  "provider" varchar DEFAULT NULL,
  "resource" varchar NOT NULL,          -- Dimension resource
  "rate" numeric NOT NULL,              -- Rent without discounts
  "price" numeric DEFAULT NULL,         -- Standard monthly rate
  "stay_length" varchar NULL,           -- LONG, MEDIUM, SHORT, GROUP
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT income_pk PRIMARY KEY ("id")
);

-- Create booking
CREATE TABLE gold.booking (
  "id" int8 NOT NULL,
  "status" varchar NULL,
  "who" varchar NULL,
  "referral" varchar NULL,
  "channel" varchar NULL,
  "agent" varchar NULL,
  "customer" varchar NULL,
  "email" varchar NULL,
  "phones" varchar NULL,
  "birth_date" date NULL,
  "gender" varchar NULL,
  "nationality" varchar NULL,
  "continent" varchar NULL,
  "language" varchar NULL,
  "reason" varchar NULL,
  "school" varchar NULL,
  "school_type" varchar NULL,
  "school_other" varchar NULL,
  "company" varchar NULL,
  "first_contact" date NULL,
  "request_date" date NULL,
  "confirmation_date" date NULL,
  "resource" varchar NULL,
  "stay_length" varchar NULL,
  "rent" numeric NULL,
  "services" numeric NULL,
  "total_rent" numeric NULL,
  "total_services" numeric NULL,
  "limit" numeric NULL,
  "direct_cost" numeric NULL,
  "date_from" date NULL,
  "date_to" date NULL,
  "check_in" date NULL,
  "check_out" date NULL,
  "tax" numeric NULL,
  "booking_fee" numeric NULL,
  "management_fee" numeric NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT booking_pk PRIMARY KEY ("id")
);

-- Create marketplace costs
CREATE TABLE gold.marketplace (
  "id" varchar NOT NULL,
  "booking" varchar NOT NULL,
  "marketplace" varchar NULL,
  "amount" numeric NULL,
  "date_from" date NULL,
  "date_to" date NULL,
  "count" int8 NOT NULL,
  "cost" numeric NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create general ledger
CREATE TABLE gold.gl (
  "cacc_doc_uuid" varchar NOT NULL,
  "cacc_doc_it_uuid" varchar NOT NULL,
  "cbus_part_uuid" varchar NULL,
  "ccost_ctr_uuid" varchar NULL,
  "ccreation_date" timestamp NOT NULL,
  "cdoc_date" date NULL,
  "cfiscyear" int4 NOT NULL,
  "cfiscper" int4 NOT NULL,
  "cfix_asset_uuid" varchar NULL,
  "cglacct" varchar NOT NULL,
  "cnote_hd" varchar NULL,
  "cnote_it" varchar NULL,
  "coedpartner" varchar NULL,
  "coedref_f_id" varchar NULL,
  "coff_glacct" varchar NULL,
  "cposting_date" date NOT NULL,
  "cprofitctr_uuid" varchar NULL,
  "kccredit_currcomp" numeric NULL,
  "kcdebit_currcomp" numeric NULL,
  "kcbalance_currcomp" numeric NULL,
  "tbus_part_uuid" varchar NULL,
  "tcost_ctr_uuid" varchar NULL,
  "tfix_asset_uuid" varchar NULL,
  "tglacct" varchar NULL,
  "toff_glacct" varchar NULL,
  "tproduct_type" varchar NULL,
  "tproduct_uuid" varchar NULL,
  "tprofitctr_uuid" varchar NULL,
  "ts" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT gl_pk PRIMARY KEY ("cfiscyear","cacc_doc_uuid", "cacc_doc_it_uuid")
);
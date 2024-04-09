-- Drop tables
DROP TABLE IF EXISTS gold.date CASCADE;
DROP TABLE IF EXISTS gold.product CASCADE;
DROP TABLE IF EXISTS gold.owner CASCADE;
DROP TABLE IF EXISTS gold.location CASCADE;
DROP TABLE IF EXISTS gold.resource CASCADE;
DROP TABLE IF EXISTS gold.income CASCADE;

-- Create owners table
CREATE TABLE gold.owner (
  "id" varchar NOT NULL,
  "type" varchar NOT NULL,
  "name" varchar NOT NULL,
CONSTRAINT owner_pk PRIMARY KEY ("id")
);

-- Create product table
CREATE TABLE gold.product (
  "id" varchar NOT NULL,
  "type" varchar NOT NULL,
CONSTRAINT product_pk PRIMARY KEY ("id")
);

-- Create locations table
CREATE TABLE gold.location (
  "id" varchar NOT NULL,
  "province" varchar NOT NULL,
  "country" varchar NOT NULL,
CONSTRAINT location_pk PRIMARY KEY ("id")
);

-- Create resources table
CREATE TABLE gold.resource (
  "id" varchar NOT NULL,
  "owner" varchar NOT NULL,
  "location" varchar NOT NULL,
  "building" varchar NOT NULL,
  "flat" varchar DEFAULT NULL,
  "flat_type" varchar DEFAULT NULL,
  "place_type" varchar DEFAULT NULL,
CONSTRAINT resource_pk PRIMARY KEY ("id"),
CONSTRAINT resource_owner_fk FOREIGN KEY ("owner") REFERENCES gold.owner("id"),
CONSTRAINT resource_location_fk FOREIGN KEY ("location") REFERENCES gold.location("id")
);

-- Create dates table
CREATE TABLE gold.date (
  "date" date NOT NULL,
  "day" int2 NOT NULL,
  "dow" int2 NOT NULL,
  "downame" varchar NOT NULL,
  "week" int2 NOT NULL,
  "month" int2 NOT NULL,
  "monthname" varchar NOT NULL,
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

-- Create income table
CREATE TABLE gold.income (
  "id" varchar NOT NULL,                -- Record id
  "doc_id" varchar NOT NULL,            -- Id of the income document (invoice, ...)
  "doc_type" varchar NOT NULL,          -- Document type
  "booking" int8 DEFAULT NULL,          -- Booking id
  "date" date NOT NULL,                 -- Date of the income
  "provider" varchar DEFAULT NULL,
  "resource" varchar NOT NULL,
  "product" varchar NOT NULL,
  "amount" decimal(10, 2) NOT NULL,
  "rate" decimal(10, 2) NOT NULL,
  "discount" decimal(5, 2) NOT NULL,
  "income_type" varchar NOT NULL,       -- B2B, B2C, ...
  "data_type" varchar NOT NULL,         -- Real, OTB, Forecast...
CONSTRAINT income_pk PRIMARY KEY ("id")
);

-- Insert dates
INSERT INTO gold."date" (
  "date", "day", "dow", "downame", "week", "month", "monthname", "year", "quarter", "quartername", 
  "semester", "semestername", "yearsemester", "yearquarter", "yearmonth", "yearweek"
)
SELECT
  d::DATE AS "date",
  EXTRACT(DAY FROM d) AS "day",
  EXTRACT(ISODOW FROM d) AS "dow",
  (ARRAY['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])[EXTRACT(ISODOW FROM d)],
  EXTRACT(WEEK FROM d) AS "week",
  EXTRACT(MONTH FROM d) AS "month",
  (ARRAY['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])[EXTRACT(MONTH FROM d)] AS "monthname",
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
  generate_series('2024-01-01'::DATE, '2025-12-31'::DATE, '1 day') AS d;
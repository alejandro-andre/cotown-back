-- Actualizacion planificada de status
BEGIN

UPDATE "Resource"."Resource" r
SET "Status_id" = subquery."Current_status_id"
FROM (
  SELECT r.id, 
    CASE 
      WHEN r."Resource_type" IN ('habitacion', 'plaza') THEN NULL
      WHEN ra."Status_id" IS NULL AND r."Resource_type" = 'piso' THEN 1
      ELSE COALESCE(ra."Status_id", 2) 
    END AS "Current_status_id"
  FROM "Resource"."Resource" r
  LEFT JOIN "Resource"."Resource_availability" ra ON ra."Resource_id" = r.id AND "Date_from" <= current_date AND "Date_to" >= current_date
) subquery
WHERE r.id = subquery.id
  AND COALESCE(r."Status_id", 0) <> COALESCE(subquery."Current_status_id", 0);
  
END;
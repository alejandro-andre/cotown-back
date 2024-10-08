SELECT 
  r."Code" AS "Resource.Code", 
  ra."Date_from", 
  ra."Date_to", 
  rs."Name" AS "Status.Name"
FROM "Resource"."Resource_availability" ra
  INNER JOIN "Resource"."Resource" r ON r.id = ra."Resource_id"
  INNER JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
ORDER BY 1, 2
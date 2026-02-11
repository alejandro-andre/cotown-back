SELECT
  b.id, 
  c."Name",
  b."Date_from", b."Date_to",
  cr."Name" AS "Motivo",
  COALESCE(STRING_AGG(DISTINCT cdt."Name", ', ' ORDER BY cdt."Name"), 'Sin documentos') AS "Documentos"
FROM "Booking"."Booking" b
  LEFT JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
  LEFT JOIN "Booking"."Customer_reason" cr ON cr.id = b."Reason_id"
  LEFT JOIN "Customer"."Customer_doc" cd ON cd."Customer_id" = b."Customer_id" AND (cd."Document").name IS NOT NULL
  LEFT JOIN "Customer"."Customer_doc_type" cdt ON cdt.id = cd."Customer_doc_type_id" AND cdt.id IN (6, 7, 11, 12)
WHERE b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
  AND b."Date_from" < %(fhasta)s AND b."Date_to" >= %(fdesde)s
GROUP BY 1, 2, 3, 4, 5
ORDER BY b.id
;

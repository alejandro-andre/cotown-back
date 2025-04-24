SELECT 
  bo.id, bo."Date_from", bo."Date_to", bo."Date_estimated", 
  p."Name" as "Product_name", bo."Rent", m."Name" AS "Month", bo."IPC_updated",
  bo."Deposit", bo."Deposit_required", bo."Deposit_returned", bo."Deposit_return_date",
  bo."Compensation", bo."Compensation_date",
  bo."Extras", bo."Extras_concept", bo."Debts", bo."Warrants", 
  bo."Include_gas", bo."Include_electricity", bo."Include_water",
  bo."Contribution_percent", bo."Contribution_recommended", bo."Contribution_asking", 
  bo."Contribution_proposal", bo."Contribution_proposed_date", bo."Contribution_comments",
  bo."Comments",
  bu."Name" AS "Building_name", r."Code", r."SAP_code",
  c."Name" AS "Customer_name", c."Document", c."Phones",
  bs."Name" AS "Status_name",
  CASE
    WHEN bo."Unlawful" THEN 'Yes'
    ELSE ''
  END AS "Unlawful", 
  CASE
    WHEN bo."Unlawful" AND bo."Bill_unlawful" THEN 'Yes'
    WHEN bo."Unlawful" AND NOT bo."Bill_unlawful" THEN 'No'
    ELSE ''
  END AS "Bill_unlawful"
FROM "Booking"."Booking_other" bo 
  INNER JOIN "Resource"."Resource" r ON r.id = bo."Resource_id"
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id" 
  INNER JOIN "Customer"."Customer" c ON c.id = bo."Customer_id" 
  INNER JOIN "Booking"."Booking_subtype" bs ON bs.id = bo."Substatus_id" 
  INNER JOIN "Billing"."Product" p ON p.id = bo."Product_id"
  INNER JOIN "Auxiliar"."Monthname" m on m.id = bo."IPC_month"
WHERE bo."Substatus_id" <> 6
;
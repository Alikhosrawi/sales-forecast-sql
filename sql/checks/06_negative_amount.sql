-- check: dq_negative_amount
-- severity: WARN
-- description: Deal amounts are not negative.
SELECT DISTINCT 'dq_negative_amount' AS check_id, 'WARN' AS severity, deal_id,
       'Amount is ' || eur(amount_eur) || '; excluded from the forecast until fixed' AS detail
FROM snap_raw
WHERE which = 'curr' AND amount_eur < 0

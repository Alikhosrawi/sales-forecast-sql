-- check: dq_missing_amount
-- severity: WARN
-- description: Open deals have an amount.
SELECT DISTINCT 'dq_missing_amount' AS check_id, 'WARN' AS severity, deal_id,
       'Open deal has no amount; counted as €0 until the rep fills it in' AS detail
FROM snap_raw
WHERE which = 'curr' AND amount_eur IS NULL
  AND stage NOT IN ('Closed Won', 'Closed Lost')

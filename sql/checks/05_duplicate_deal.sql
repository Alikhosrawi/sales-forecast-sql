-- check: dq_duplicate_deal
-- severity: WARN
-- description: Each deal appears once in the CRM export and once per weekly snapshot.
SELECT 'dq_duplicate_deal' AS check_id, 'WARN' AS severity, deal_id,
       'Deal appears ' || count(*) || ' times in the CRM deals export' AS detail
FROM deals GROUP BY deal_id HAVING count(*) > 1
UNION ALL
SELECT 'dq_duplicate_deal', 'WARN', deal_id,
       'Deal appears ' || count(*) || ' times in this week''s snapshot'
FROM snap_raw WHERE which = 'curr' GROUP BY deal_id HAVING count(*) > 1

-- check: dq_missing_quota
-- severity: BLOCKER
-- description: Every rep has a positive quarterly quota (attainment and gap are meaningless without it).
SELECT 'dq_missing_quota' AS check_id, 'BLOCKER' AS severity, CAST(NULL AS VARCHAR) AS deal_id,
       'Rep ' || rep_id || ' (' || name || ') has no valid quota' AS detail
FROM reps
WHERE quota_q IS NULL OR quota_q <= 0

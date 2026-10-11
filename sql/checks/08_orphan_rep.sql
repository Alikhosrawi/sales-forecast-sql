-- check: dq_orphan_rep
-- severity: WARN
-- description: Every deal owner exists in the reps table.
SELECT DISTINCT 'dq_orphan_rep' AS check_id, 'WARN' AS severity, d.deal_id,
       'Owner "' || coalesce(d.rep_id, '(blank)') || '" is not in the reps table; shown under Unassigned' AS detail
FROM deals d
WHERE d.rep_id IS NULL OR d.rep_id NOT IN (SELECT rep_id FROM reps)

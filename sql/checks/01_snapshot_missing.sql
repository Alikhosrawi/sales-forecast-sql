-- check: dq_snapshot_missing
-- severity: BLOCKER
-- description: A snapshot exists for this week and for last week (no snapshot = nothing to forecast or compare).
SELECT 'dq_snapshot_missing' AS check_id, 'BLOCKER' AS severity, CAST(NULL AS VARCHAR) AS deal_id,
       'No deal snapshot for ' || w.label || ' (' || strftime(w.wk, '%G-W%V') || ')' AS detail
FROM (SELECT 'this week' AS label, run_week AS wk FROM params
      UNION ALL SELECT 'last week', prev_week FROM params) w
WHERE NOT EXISTS (SELECT 1 FROM deal_history h WHERE h.snapshot_week = w.wk)

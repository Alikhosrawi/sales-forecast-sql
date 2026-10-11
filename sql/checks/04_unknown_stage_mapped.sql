-- check: dq_unknown_stage_mapped
-- severity: WARN
-- description: Stage names match the current stage list (legacy names are translated via stage_aliases.csv).
SELECT DISTINCT 'dq_unknown_stage_mapped' AS check_id, 'WARN' AS severity, s.deal_id,
       'Stage "' || s.stage || '" is a legacy name; read as "' || a.stage || '"' AS detail
FROM snap_raw s
JOIN stage_aliases a ON a.raw_stage = s.stage
WHERE s.which = 'curr'
  AND s.stage NOT IN (SELECT stage FROM stages)

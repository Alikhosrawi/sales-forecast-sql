-- check: dq_unknown_stage_unmapped
-- severity: BLOCKER
-- description: Every stage name is known or has a documented alias (otherwise there is no probability to apply).
SELECT DISTINCT 'dq_unknown_stage_unmapped' AS check_id, 'BLOCKER' AS severity, s.deal_id,
       'Stage "' || s.stage || '" is not a known stage and has no alias in data/seeds/stage_aliases.csv' AS detail
FROM snap_raw s
WHERE s.stage NOT IN (SELECT stage FROM stages)
  AND s.stage NOT IN (SELECT raw_stage FROM stage_aliases)

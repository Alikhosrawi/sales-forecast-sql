-- Fix for dq_unknown_stage_mapped: translate legacy stage names using the
-- documented alias list (data/seeds/stage_aliases.csv). Unmapped names never
-- reach this step: they are a BLOCKER.
INSERT INTO clean_log
SELECT 'stage_alias', s.deal_id, s.which || ' snapshot',
       'Stage "' || s.stage || '" read as "' || a.stage || '"'
FROM snap_1 s JOIN stage_aliases a ON a.raw_stage = s.stage
WHERE s.stage NOT IN (SELECT stage FROM stages);

CREATE OR REPLACE TABLE snap_2 AS
SELECT s.* REPLACE (CASE WHEN s.stage IN (SELECT stage FROM stages) THEN s.stage
                         ELSE a.stage END AS stage)
FROM snap_1 s
LEFT JOIN stage_aliases a ON a.raw_stage = s.stage;

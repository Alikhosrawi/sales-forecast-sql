-- Fix for dq_orphan_rep: deals whose owner is not in the reps table are kept
-- (the money is real) but shown under an "Unassigned" owner with no quota, so
-- they count for the team total but not for any one rep.
INSERT INTO clean_log
SELECT 'orphan_rep', deal_id, 'deals export',
       'Owner "' || coalesce(rep_id, '(blank)') || '" not found; moved to UNASSIGNED'
FROM deals_1
WHERE rep_id IS NULL OR rep_id NOT IN (SELECT rep_id FROM reps);

CREATE OR REPLACE TABLE reps_clean AS
SELECT rep_id, name, team, CAST(quota_q AS DECIMAL(18,2)) AS quota_q FROM reps
UNION ALL
SELECT 'UNASSIGNED', 'Unassigned', 'Unassigned', CAST(0 AS DECIMAL(18,2));

CREATE OR REPLACE TABLE deals_2 AS
SELECT d.* REPLACE (CASE WHEN d.rep_id IN (SELECT rep_id FROM reps) THEN d.rep_id
                         ELSE 'UNASSIGNED' END AS rep_id)
FROM deals_1 d;

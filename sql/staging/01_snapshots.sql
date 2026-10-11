-- The two snapshots the run compares: this week ('curr') and last week ('prev').
-- Raw = exactly as exported from the CRM; checks look at this, clean/ fixes it.
CREATE OR REPLACE TABLE snap_raw AS
SELECT 'curr' AS which, h.*
FROM deal_history h, params p
WHERE h.snapshot_week = p.run_week
UNION ALL
SELECT 'prev' AS which, h.*
FROM deal_history h, params p
WHERE h.snapshot_week = p.prev_week;

-- Full history up to the run week (never look into the future), with legacy
-- stage names translated. Used for win rates and risk signals.
CREATE OR REPLACE TABLE hist_mapped AS
SELECT DISTINCT
    h.deal_id,
    h.snapshot_week,
    coalesce(a.stage, h.stage) AS stage,
    h.amount_eur,
    h.close_date
FROM deal_history h
LEFT JOIN stage_aliases a ON a.raw_stage = h.stage
CROSS JOIN params p
WHERE h.snapshot_week <= p.run_week;

-- Activities known at the time of the run.
CREATE OR REPLACE TABLE last_activity AS
SELECT a.deal_id, max(a.occurred_at) AS last_activity_at
FROM activities a, params p
WHERE a.occurred_at <= p.as_of
GROUP BY a.deal_id;

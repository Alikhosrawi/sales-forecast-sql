-- Forecast vs quota by rep, this week.
--   commit    = closed won + open deals the rep marked "commit"
--   best case = commit + open deals marked "best_case"
--   pipeline  = open deals marked "pipeline" (unweighted)
--   forecast  = closed won + weighted open pipeline (the headline number)
CREATE OR REPLACE TABLE rep_forecast AS
WITH v AS (SELECT * FROM deal_values WHERE which = 'curr' AND in_quarter)
SELECT
    r.rep_id,
    r.name AS rep_name,
    r.team,
    r.quota_q,
    CAST(coalesce(sum(v.amount_eur) FILTER (WHERE v.status = 'won'), 0) AS DECIMAL(18,2))                                AS closed_won,
    CAST(coalesce(sum(v.amount_eur) FILTER (WHERE v.status = 'open' AND v.forecast_category = 'commit'), 0) AS DECIMAL(18,2))    AS commit_open,
    CAST(coalesce(sum(v.amount_eur) FILTER (WHERE v.status = 'open' AND v.forecast_category = 'best_case'), 0) AS DECIMAL(18,2)) AS best_case_open,
    CAST(coalesce(sum(v.amount_eur) FILTER (WHERE v.status = 'open' AND v.forecast_category = 'pipeline'), 0) AS DECIMAL(18,2))  AS pipeline_open,
    CAST(coalesce(sum(v.weighted_value) FILTER (WHERE v.status = 'open'), 0) AS DECIMAL(18,2))                          AS weighted_open,
    count(v.deal_id) FILTER (WHERE v.status = 'open')                                                                   AS open_deals
FROM reps_clean r
LEFT JOIN v ON v.rep_id = r.rep_id
GROUP BY ALL;

CREATE OR REPLACE TABLE rep_forecast AS
SELECT
    *,
    closed_won + commit_open                         AS commit_total,
    closed_won + commit_open + best_case_open        AS best_case_total,
    closed_won + weighted_open                       AS forecast,
    CASE WHEN quota_q > 0 THEN round(100 * closed_won / quota_q, 1) END                   AS attainment_pct,
    CASE WHEN quota_q > 0 THEN quota_q - closed_won END                                   AS gap_to_quota,
    CASE WHEN quota_q > 0 THEN round(100 * (closed_won + weighted_open) / quota_q, 1) END AS forecast_pct_of_quota
FROM rep_forecast
WHERE NOT (rep_id = 'UNASSIGNED' AND closed_won = 0 AND weighted_open = 0 AND pipeline_open + best_case_open + commit_open = 0)
ORDER BY CASE WHEN rep_id = 'UNASSIGNED' THEN 1 ELSE 0 END, team, rep_id;

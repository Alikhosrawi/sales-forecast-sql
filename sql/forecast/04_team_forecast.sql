-- Roll-up by team plus a company total. Unassigned deals count in the total.
CREATE OR REPLACE TABLE team_forecast AS
WITH t AS (
    SELECT team, 1 AS sort_key, * EXCLUDE (team, rep_id, rep_name, attainment_pct, gap_to_quota, forecast_pct_of_quota)
    FROM rep_forecast
    UNION ALL
    SELECT 'Total', 2, * EXCLUDE (team, rep_id, rep_name, attainment_pct, gap_to_quota, forecast_pct_of_quota)
    FROM rep_forecast
)
SELECT
    team,
    sum(quota_q)          AS quota_q,
    sum(closed_won)       AS closed_won,
    sum(commit_open)      AS commit_open,
    sum(best_case_open)   AS best_case_open,
    sum(pipeline_open)    AS pipeline_open,
    sum(weighted_open)    AS weighted_open,
    sum(open_deals)       AS open_deals,
    sum(commit_total)     AS commit_total,
    sum(best_case_total)  AS best_case_total,
    sum(forecast)         AS forecast,
    CASE WHEN sum(quota_q) > 0 THEN round(100 * sum(closed_won) / sum(quota_q), 1) END AS attainment_pct,
    CASE WHEN sum(quota_q) > 0 THEN sum(quota_q) - sum(closed_won) END                 AS gap_to_quota,
    CASE WHEN sum(quota_q) > 0 THEN round(100 * sum(forecast) / sum(quota_q), 1) END   AS forecast_pct_of_quota,
    min(sort_key) AS sort_key
FROM t
GROUP BY team
ORDER BY sort_key, team;

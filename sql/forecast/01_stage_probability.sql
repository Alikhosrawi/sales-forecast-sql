-- Probability per stage.
-- For each stage: of the deals that were ever in that stage AND closed before
-- this quarter started, what share was won? If at least 10 such deals exist we
-- trust that historical win rate; otherwise we fall back to the default
-- probability from the stages table. The table says which one was used.
-- Only data from before the quarter is used, so the probabilities stay fixed
-- for every week of the quarter and week-over-week moves are real moves.
CREATE OR REPLACE TABLE stage_probability AS
WITH final_state AS (
    SELECT deal_id,
           max_by(stage, snapshot_week)      AS final_stage,
           max_by(close_date, snapshot_week) AS final_close
    FROM hist_mapped
    GROUP BY deal_id
),
closed_before_q AS (
    SELECT f.* FROM final_state f, params p
    WHERE f.final_stage IN ('Closed Won', 'Closed Lost')
      AND f.final_close < p.q_start
),
reached AS (
    SELECT DISTINCT h.deal_id, h.stage, c.final_stage
    FROM hist_mapped h JOIN closed_before_q c USING (deal_id)
),
rates AS (
    SELECT stage,
           count(*)                                          AS n,
           count(*) FILTER (WHERE final_stage = 'Closed Won') AS won
    FROM reached GROUP BY stage
)
SELECT
    s.stage,
    s.order_index,
    CAST(s.default_probability AS DECIMAL(6,4))                         AS default_probability,
    coalesce(r.n, 0)                                                    AS hist_n,
    coalesce(r.won, 0)                                                  AS hist_won,
    CASE WHEN r.n > 0 THEN CAST(round(r.won / r.n, 4) AS DECIMAL(6,4)) END AS hist_win_rate,
    CAST(CASE WHEN s.stage IN ('Closed Won', 'Closed Lost') THEN s.default_probability
              WHEN coalesce(r.n, 0) >= 10 THEN round(r.won / r.n, 4)
              ELSE s.default_probability END AS DECIMAL(6,4))           AS probability_used,
    CASE WHEN s.stage IN ('Closed Won', 'Closed Lost') THEN 'fixed (closed)'
         WHEN coalesce(r.n, 0) >= 10 THEN 'historical win rate (n=' || r.n || ')'
         ELSE 'default (only ' || coalesce(r.n, 0) || ' closed deals, need 10)' END AS source
FROM stages s
LEFT JOIN rates r USING (stage)
ORDER BY s.order_index;

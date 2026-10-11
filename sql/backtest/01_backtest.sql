-- Backtest the two quarters before the run quarter.
-- Week 6 is the 6th Monday snapshot inside that quarter. The forecast uses the
-- same rules as sql/forecast: a historical win rate when at least 10 deals
-- closed before the quarter had reached the stage, otherwise the default.
-- Won and due that quarter counts in full; an open deal due that quarter
-- counts as amount x probability, rounded to the cent.
-- Actual is the closed-won total with a close date in the quarter, from the
-- latest snapshot (the result the quarter finished with).
-- error = forecast - actual. Positive means the week-6 forecast was high.
CREATE OR REPLACE TABLE backtest AS
WITH quarters AS (
    SELECT CAST(CAST(date_trunc('quarter', p.run_week) AS DATE) - (n * INTERVAL 3 MONTH) AS DATE) AS q_start
    FROM params p, (SELECT unnest([1, 2]) AS n) s
),
bounds AS (
    SELECT
        q_start,
        CAST(q_start + INTERVAL 3 MONTH - INTERVAL 1 DAY AS DATE) AS q_end,
        'Q' || ((month(q_start) - 1) // 3 + 1) || ' ' || year(q_start) AS quarter_label
    FROM quarters
),
week_nos AS (
    SELECT q_start, snapshot_week,
           row_number() OVER (PARTITION BY q_start ORDER BY snapshot_week) AS rn
    FROM (
        SELECT DISTINCT b.q_start, h.snapshot_week
        FROM bounds b
        JOIN deal_history h ON h.snapshot_week BETWEEN b.q_start AND b.q_end
    )
),
ready AS (
    SELECT b.q_start, b.q_end, b.quarter_label, w.snapshot_week AS as_of_week
    FROM bounds b
    JOIN week_nos w ON w.q_start = b.q_start AND w.rn = 6
),
mapped_hist AS (
    SELECT
        h.deal_id,
        h.snapshot_week,
        coalesce(a.stage, h.stage) AS stage,
        h.amount_eur,
        h.close_date
    FROM deal_history h
    LEFT JOIN stage_aliases a ON a.raw_stage = h.stage
),
final_state AS (
    SELECT deal_id,
           max_by(stage, snapshot_week)      AS final_stage,
           max_by(close_date, snapshot_week) AS final_close
    FROM mapped_hist
    GROUP BY deal_id
),
closed_before AS (
    SELECT r.q_start, f.deal_id, f.final_stage
    FROM ready r
    JOIN final_state f
      ON f.final_stage IN ('Closed Won', 'Closed Lost')
     AND f.final_close < r.q_start
),
reached AS (
    SELECT DISTINCT c.q_start, h.deal_id, h.stage, c.final_stage
    FROM closed_before c
    JOIN mapped_hist h ON h.deal_id = c.deal_id
),
rates AS (
    SELECT q_start, stage,
           count(*) AS n,
           count(*) FILTER (WHERE final_stage = 'Closed Won') AS won
    FROM reached
    GROUP BY q_start, stage
),
probs AS (
    SELECT
        r.q_start,
        s.stage,
        CAST(CASE
            WHEN s.stage IN ('Closed Won', 'Closed Lost') THEN s.default_probability
            WHEN coalesce(rt.n, 0) >= 10 THEN round(rt.won / rt.n, 4)
            ELSE s.default_probability
        END AS DECIMAL(6,4)) AS probability_used
    FROM ready r
    CROSS JOIN stages s
    LEFT JOIN rates rt ON rt.q_start = r.q_start AND rt.stage = s.stage
),
snap AS (
    SELECT DISTINCT ON (r.q_start, h.deal_id)
        r.q_start,
        r.q_end,
        r.quarter_label,
        r.as_of_week,
        h.deal_id,
        CASE WHEN h.stage IN (SELECT stage FROM stages) THEN h.stage ELSE a.stage END AS stage,
        h.amount_eur,
        h.close_date
    FROM ready r
    JOIN deal_history h ON h.snapshot_week = r.as_of_week
    LEFT JOIN stage_aliases a ON a.raw_stage = h.stage
    ORDER BY r.q_start, h.deal_id, h.amount_eur DESC NULLS LAST, h.close_date, h.stage
),
snap_ok AS (
    SELECT * REPLACE (CAST(coalesce(amount_eur, 0) AS DECIMAL(18,2)) AS amount_eur)
    FROM snap
    WHERE stage IS NOT NULL
      AND (amount_eur IS NULL OR amount_eur >= 0)
),
valued AS (
    SELECT
        s.q_start,
        s.quarter_label,
        s.as_of_week,
        CAST(CASE
            WHEN s.close_date BETWEEN s.q_start AND s.q_end AND s.stage = 'Closed Won' THEN s.amount_eur
            WHEN s.close_date BETWEEN s.q_start AND s.q_end
                 AND s.stage NOT IN ('Closed Won', 'Closed Lost')
                THEN round(s.amount_eur * p.probability_used, 2)
            ELSE 0
        END AS DECIMAL(18,2)) AS weighted_value
    FROM snap_ok s
    JOIN probs p ON p.q_start = s.q_start AND p.stage = s.stage
),
forecasts AS (
    SELECT q_start, quarter_label, as_of_week,
           CAST(coalesce(sum(weighted_value), 0) AS DECIMAL(18,2)) AS forecast_eur
    FROM valued
    GROUP BY q_start, quarter_label, as_of_week
),
latest AS (
    SELECT DISTINCT ON (deal_id)
        deal_id, stage, amount_eur, close_date
    FROM mapped_hist
    ORDER BY deal_id, snapshot_week DESC, amount_eur DESC NULLS LAST, close_date, stage
),
actuals AS (
    SELECT r.q_start,
           CAST(coalesce(sum(l.amount_eur), 0) AS DECIMAL(18,2)) AS actual_eur
    FROM ready r
    LEFT JOIN latest l
      ON l.stage = 'Closed Won'
     AND l.close_date BETWEEN r.q_start AND r.q_end
    GROUP BY r.q_start
)
SELECT
    f.quarter_label,
    f.q_start AS quarter_start,
    f.as_of_week,
    strftime(f.as_of_week, '%G-W%V') AS as_of_label,
    f.forecast_eur,
    a.actual_eur,
    CAST(f.forecast_eur - a.actual_eur AS DECIMAL(18,2)) AS error_eur,
    CASE WHEN a.actual_eur = 0 THEN NULL
         ELSE CAST(round(100 * (f.forecast_eur - a.actual_eur) / a.actual_eur, 1) AS DECIMAL(8,1))
    END AS error_pct
FROM forecasts f
JOIN actuals a USING (q_start)
ORDER BY f.q_start;

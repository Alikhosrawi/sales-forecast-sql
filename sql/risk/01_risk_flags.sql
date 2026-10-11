-- One row per (open deal, risk signal), each with a plain-English reason.
CREATE OR REPLACE TABLE risk_flags AS
WITH open_now AS (
    SELECT * FROM deal_values WHERE which = 'curr' AND status = 'open'
),
hist AS (
    SELECT h.*,
           st.order_index,
           lag(h.close_date)   OVER w AS prev_close,
           lag(st.order_index) OVER w AS prev_order,
           lag(h.stage)        OVER w AS prev_stage,
           first_value(h.close_date) OVER (PARTITION BY h.deal_id ORDER BY h.snapshot_week) AS first_close
    FROM hist_mapped h
    JOIN stages st ON st.stage = h.stage
    WINDOW w AS (PARTITION BY h.deal_id ORDER BY h.snapshot_week)
),
pushes AS (
    SELECT deal_id, count(*) AS n_pushes, any_value(first_close) AS first_close
    FROM hist WHERE close_date > prev_close GROUP BY deal_id
),
backwards AS (
    SELECT h.deal_id,
           arg_max(h.prev_stage || ' to ' || h.stage, h.snapshot_week) AS last_move,
           max(h.snapshot_week) AS moved_week
    FROM hist h, params p
    WHERE h.order_index < h.prev_order AND h.prev_order <= 5
      AND h.snapshot_week >= p.q_start
    GROUP BY h.deal_id
),
peak AS (
    SELECT h.deal_id, max(h.amount_eur) AS peak_amount
    FROM hist h, params p
    WHERE h.snapshot_week >= p.q_start AND h.amount_eur > 0
    GROUP BY h.deal_id
)
-- 1) close date pushed 2+ times
SELECT o.deal_id, 'pushed_2x' AS flag, 1 AS flag_order,
       'Close date pushed ' || pu.n_pushes || ' times (first ' || strftime(pu.first_close, '%d %b') ||
       ', now ' || strftime(o.close_date, '%d %b') || ')' AS reason
FROM open_now o JOIN pushes pu USING (deal_id)
WHERE pu.n_pushes >= 2
UNION ALL
-- 2) no activity for 14+ days
SELECT o.deal_id, 'no_activity_14d', 2,
       CASE WHEN la.last_activity_at IS NULL THEN 'No activity ever logged'
            ELSE 'No activity for ' || (p.as_of - la.last_activity_at) || ' days' END
FROM open_now o
CROSS JOIN params p
JOIN deals_2 d USING (deal_id)
LEFT JOIN last_activity la USING (deal_id)
WHERE d.created_at <= p.as_of - 14
  AND (la.last_activity_at IS NULL OR la.last_activity_at < p.as_of - 14)
UNION ALL
-- 3) stage moved backwards this quarter
SELECT o.deal_id, 'stage_backwards', 3,
       'Moved back from ' || b.last_move || ' (week of ' || strftime(b.moved_week, '%d %b') || ')'
FROM open_now o JOIN backwards b USING (deal_id)
UNION ALL
-- 4) amount cut by 20% or more vs its peak this quarter
SELECT o.deal_id, 'amount_cut_20', 4,
       'Amount cut ' || CAST(round(100 * (1 - o.amount_eur / pk.peak_amount)) AS INTEGER) || '% (from ' ||
       eur(pk.peak_amount) || ' to ' || eur(o.amount_eur) || ')'
FROM open_now o JOIN peak pk USING (deal_id)
WHERE o.amount_eur > 0 AND o.amount_eur <= 0.8 * pk.peak_amount
UNION ALL
-- 5) supposed to close this quarter but still in an early stage
SELECT o.deal_id, 'early_stage_this_q', 5,
       'Due to close ' || strftime(o.close_date, '%d %b') || ' but still in ' || o.stage
FROM open_now o
WHERE o.in_quarter AND o.order_index <= 2;

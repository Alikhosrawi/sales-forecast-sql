-- The clean, enriched snapshot that every later step reads.
CREATE OR REPLACE TABLE snap_clean AS
SELECT
    s.which,
    s.deal_id,
    d.name                                     AS deal_name,
    d.account_id,
    coalesce(d.rep_id, 'UNASSIGNED')           AS rep_id,
    coalesce(r.name, 'Unassigned')             AS rep_name,
    coalesce(r.team, 'Unassigned')             AS team,
    s.stage,
    st.order_index,
    CASE s.stage WHEN 'Closed Won' THEN 'won' WHEN 'Closed Lost' THEN 'lost' ELSE 'open' END AS status,
    CAST(s.amount_eur AS DECIMAL(18,2))        AS amount_eur,
    s.close_date,
    s.forecast_category,
    (s.close_date BETWEEN p.q_start AND p.q_end) AS in_quarter
FROM snap_3 s
CROSS JOIN params p
JOIN stages st ON st.stage = s.stage
LEFT JOIN deals_2 d ON d.deal_id = s.deal_id
LEFT JOIN reps_clean r ON r.rep_id = coalesce(d.rep_id, 'UNASSIGNED');

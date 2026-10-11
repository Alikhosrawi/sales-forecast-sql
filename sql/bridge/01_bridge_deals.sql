-- Week-over-week bridge, deal by deal.
-- Every deal's change (this week's value - last week's value) is assigned to
-- exactly one bucket, except deals that stayed open in the quarter, whose
-- change is split in two:
--   amount effect = (new amount - old amount) x last week's probability
--   stage effect  = whatever is left (so the two always add up exactly)
-- Because every cent of every deal's change lands in some bucket, the buckets
-- sum to the total change by construction. tests/test_bridge.py checks it.
CREATE OR REPLACE TABLE bridge_deals AS
WITH p AS (SELECT * FROM deal_values WHERE which = 'prev'),
     c AS (SELECT * FROM deal_values WHERE which = 'curr'),
j AS (
    SELECT
        coalesce(c.deal_id, p.deal_id)                AS deal_id,
        coalesce(c.deal_name, p.deal_name)            AS deal_name,
        p.deal_id IS NOT NULL                         AS in_prev,
        c.deal_id IS NOT NULL                         AS in_curr,
        p.status AS prev_status, c.status AS curr_status,
        p.in_quarter AS prev_inq, c.in_quarter AS curr_inq,
        p.stage AS prev_stage, c.stage AS curr_stage,
        p.amount_eur AS prev_amount, c.amount_eur AS curr_amount,
        p.prob AS prev_prob,
        coalesce(p.weighted_value, 0)                 AS prev_value,
        coalesce(c.weighted_value, 0)                 AS curr_value
    FROM p FULL OUTER JOIN c ON c.deal_id = p.deal_id
),
classified AS (
    SELECT j.*,
        CASE
            WHEN in_curr AND NOT in_prev THEN
                CASE WHEN j.deal_id IN (SELECT deal_id FROM snap_raw WHERE which = 'prev')
                     THEN 'data_fixes' ELSE 'new' END
            WHEN in_prev AND NOT in_curr THEN
                CASE WHEN j.deal_id IN (SELECT deal_id FROM snap_raw WHERE which = 'curr')
                     THEN 'data_fixes' ELSE 'other' END
            WHEN prev_status = 'open' AND curr_status = 'won'  THEN 'won'
            WHEN prev_status = 'open' AND curr_status = 'lost' THEN 'lost'
            WHEN prev_status = 'open' AND curr_status = 'open' THEN
                CASE WHEN prev_inq AND NOT curr_inq THEN 'slipped'
                     WHEN curr_inq AND NOT prev_inq THEN 'pulled_in'
                     WHEN prev_inq AND curr_inq     THEN 'split'
                     ELSE 'none' END
            ELSE 'other'
        END AS kind
    FROM j
),
amount_part AS (
    SELECT deal_id,
           CASE WHEN prev_stage = curr_stage THEN curr_value - prev_value
                ELSE CAST(round((curr_amount - prev_amount) * prev_prob, 2) AS DECIMAL(18,2)) END AS amount_delta
    FROM classified WHERE kind = 'split'
)
SELECT c.deal_id, c.deal_name, c.kind AS bucket, c.prev_value, c.curr_value,
       CAST(c.curr_value - c.prev_value AS DECIMAL(18,2)) AS delta
FROM classified c
WHERE c.kind NOT IN ('split', 'none')
UNION ALL
SELECT c.deal_id, c.deal_name,
       CASE WHEN c.curr_amount > c.prev_amount THEN 'amount_up' ELSE 'amount_down' END,
       c.prev_value, c.curr_value, a.amount_delta
FROM classified c JOIN amount_part a USING (deal_id)
WHERE c.curr_amount <> c.prev_amount
UNION ALL
SELECT c.deal_id, c.deal_name, 'stage_moves', c.prev_value, c.curr_value,
       CAST(c.curr_value - c.prev_value - a.amount_delta AS DECIMAL(18,2))
FROM classified c JOIN amount_part a USING (deal_id)
WHERE c.prev_stage <> c.curr_stage;

-- The bridge as a leader reads it: last week's number, the buckets, this week's number.
CREATE OR REPLACE TABLE bridge_buckets AS
SELECT * FROM (VALUES
    (1,  'new',         'New deals',                         '1 new deal was added',               '{n} new deals were added', 'new deals'),
    (2,  'pulled_in',   'Pulled into the quarter',           '1 deal was pulled into the quarter', '{n} deals were pulled into the quarter', 'deals pulled in'),
    (3,  'won',         'Won (moved to 100%)',               '1 deal was won',                     '{n} deals were won', 'wins'),
    (4,  'lost',        'Lost',                              '1 deal was lost',                    '{n} deals were lost', 'losses'),
    (5,  'slipped',     'Slipped out of the quarter',        '1 deal slipped out of the quarter',  '{n} deals slipped out of the quarter', 'slipped deals'),
    (6,  'amount_up',   'Amount increased',                  '1 deal''s amount went up',           'amounts went up on {n} deals', 'higher amounts'),
    (7,  'amount_down', 'Amount decreased',                  '1 deal''s amount was cut',           'amounts were cut on {n} deals', 'lower amounts'),
    (8,  'stage_moves', 'Stage moves',                       '1 deal changed stage',               '{n} deals changed stage', 'stage moves'),
    (9,  'data_fixes',  'Excluded/restored by data checks',  '1 deal was affected by data checks', '{n} deals were affected by data checks', 'data-check exclusions'),
    (10, 'other',       'Other (deleted or reopened deals)', '1 other change',                     '{n} other changes', 'other changes')
) AS t(bucket_order, bucket, label, clause_one, clause_many, short_label);

CREATE OR REPLACE TABLE bridge_summary AS
WITH agg AS (
    SELECT bucket,
           sum(delta)                AS amount,
           count(DISTINCT deal_id) FILTER (WHERE delta <> 0) AS deals,
           arg_max(deal_name, abs(delta)) FILTER (WHERE delta <> 0) AS biggest_deal,
           max(abs(delta))           AS biggest_abs
    FROM bridge_deals GROUP BY bucket
)
SELECT b.bucket_order, b.bucket, b.label, b.clause_one, b.clause_many, b.short_label,
       CAST(coalesce(a.amount, 0) AS DECIMAL(18,2)) AS amount,
       coalesce(a.deals, 0)                         AS deals,
       a.biggest_deal
FROM bridge_buckets b
LEFT JOIN agg a USING (bucket)
ORDER BY b.bucket_order;

CREATE OR REPLACE TABLE bridge_totals AS
SELECT
    (SELECT CAST(sum(weighted_value) AS DECIMAL(18,2)) FROM deal_values WHERE which = 'prev') AS prev_forecast,
    (SELECT CAST(sum(weighted_value) AS DECIMAL(18,2)) FROM deal_values WHERE which = 'curr') AS curr_forecast,
    (SELECT CAST(sum(amount) AS DECIMAL(18,2)) FROM bridge_summary)                           AS bucket_sum;

CREATE OR REPLACE TABLE bridge_totals AS
SELECT *, curr_forecast - prev_forecast AS total_change,
       bucket_sum - (curr_forecast - prev_forecast) AS unexplained
FROM bridge_totals;

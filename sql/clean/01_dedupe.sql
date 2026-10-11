-- Fix for dq_duplicate_deal: keep one row per deal (per snapshot week).
-- If duplicates ever disagree, the row with the larger amount is kept and the
-- choice is logged, so the result never depends on file order.
CREATE OR REPLACE TABLE clean_log (step VARCHAR, deal_id VARCHAR, scope VARCHAR, action VARCHAR);

INSERT INTO clean_log
SELECT 'dedupe', deal_id, 'deals export',
       'Removed ' || (count(*) - 1) || ' duplicate CRM record(s), kept one'
FROM deals GROUP BY deal_id HAVING count(*) > 1;

INSERT INTO clean_log
SELECT 'dedupe', deal_id, which || ' snapshot',
       'Removed ' || (count(*) - 1) || ' duplicate snapshot row(s), kept one'
FROM snap_raw GROUP BY deal_id, which HAVING count(*) > 1;

CREATE OR REPLACE TABLE deals_1 AS
SELECT DISTINCT ON (deal_id) *
FROM deals
ORDER BY deal_id, amount_eur DESC NULLS LAST, close_date, stage;

CREATE OR REPLACE TABLE snap_1 AS
SELECT DISTINCT ON (which, deal_id) *
FROM snap_raw
ORDER BY which, deal_id, amount_eur DESC NULLS LAST, close_date, stage;

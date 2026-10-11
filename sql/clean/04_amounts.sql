-- Fixes for dq_negative_amount and dq_missing_amount.
--   negative amount -> the deal is left out of the forecast (a sign typo could
--                      be +X or a credit note; we do not guess) and listed
--   missing amount  -> counted as EUR 0 (it is in the pipeline, value unknown)
INSERT INTO clean_log
SELECT 'negative_amount', deal_id, which || ' snapshot',
       'Amount ' || eur(amount_eur) || ': deal excluded from the forecast'
FROM snap_2 WHERE amount_eur < 0;

INSERT INTO clean_log
SELECT 'missing_amount', deal_id, which || ' snapshot',
       'Amount missing on an open deal: counted as €0'
FROM snap_2 WHERE amount_eur IS NULL AND stage NOT IN ('Closed Won', 'Closed Lost');

CREATE OR REPLACE TABLE snap_3 AS
SELECT * REPLACE (coalesce(amount_eur, 0) AS amount_eur)
FROM snap_2
WHERE amount_eur IS NULL OR amount_eur >= 0;

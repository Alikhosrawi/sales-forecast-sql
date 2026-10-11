-- What each deal contributes to the quarter's forecast, for both weeks.
--   won and closing this quarter  -> full amount
--   open and closing this quarter -> amount x stage probability (rounded to the cent)
--   everything else               -> 0
CREATE OR REPLACE TABLE deal_values AS
SELECT
    c.*,
    sp.probability_used AS prob,
    CAST(CASE
        WHEN c.in_quarter AND c.status = 'won'  THEN c.amount_eur
        WHEN c.in_quarter AND c.status = 'open' THEN round(c.amount_eur * sp.probability_used, 2)
        ELSE 0
    END AS DECIMAL(18,2)) AS weighted_value
FROM snap_clean c
JOIN stage_probability sp USING (stage);

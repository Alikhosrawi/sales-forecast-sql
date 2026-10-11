-- One row per flagged open deal, ranked. The ranking puts deals that count
-- toward THIS quarter first, then more warning signs, then more money at risk.
CREATE OR REPLACE TABLE deal_risk AS
WITH per_deal AS (
    SELECT
        v.deal_id, v.deal_name, v.rep_name, v.stage, v.amount_eur, v.close_date,
        v.in_quarter, v.weighted_value,
        count(*)                                          AS flag_count,
        string_agg(f.flag, ', ' ORDER BY f.flag_order)    AS flags,
        string_agg(f.reason, '; ' ORDER BY f.flag_order)  AS reasons
    FROM risk_flags f
    JOIN deal_values v ON v.deal_id = f.deal_id AND v.which = 'curr'
    GROUP BY ALL
)
SELECT *,
       row_number() OVER (ORDER BY in_quarter DESC, flag_count DESC, weighted_value DESC, deal_id) AS risk_rank
FROM per_deal
ORDER BY risk_rank;

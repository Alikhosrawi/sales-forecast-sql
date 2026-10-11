-- The one sentence a sales leader reads first, written from the bridge:
-- "Forecast is €X (commit €Y), down €Z vs last week, mainly because A and B,
--  partly offset by C."
--   drivers = the two biggest buckets pushing in the same direction as the change
--   offset  = the biggest bucket pushing the other way
CREATE OR REPLACE TABLE headline_drivers AS
WITH t AS (SELECT * FROM bridge_totals)
SELECT
    s.*,
    CASE WHEN sign(s.amount) = sign(t.total_change) THEN 'driver' ELSE 'offset' END AS role,
    row_number() OVER (
        PARTITION BY CASE WHEN sign(s.amount) = sign(t.total_change) THEN 'driver' ELSE 'offset' END
        ORDER BY abs(s.amount) DESC, s.bucket_order) AS rnk,
    CASE WHEN s.deals = 1 THEN s.clause_one ELSE replace(s.clause_many, '{n}', CAST(s.deals AS VARCHAR)) END AS clause
FROM bridge_summary s, t
WHERE s.amount <> 0;

CREATE OR REPLACE TABLE headline AS
WITH t AS (SELECT * FROM bridge_totals),
k AS (SELECT * FROM team_forecast WHERE team = 'Total'),
d AS (
    SELECT string_agg(
               clause || ' (' || eur_signed(amount) ||
               CASE WHEN rnk = 1 AND deals = 1 THEN ': ' || biggest_deal
                    WHEN rnk = 1 THEN '; biggest: ' || biggest_deal
                    ELSE '' END || ')',
               ' and ' ORDER BY rnk) AS txt
    FROM headline_drivers WHERE role = 'driver' AND rnk <= 2
),
o AS (
    SELECT short_label || ' (' || eur_signed(amount) ||
           CASE WHEN deals > 1 THEN ' across ' || deals || ' deals' ELSE '' END || ')' AS txt
    FROM headline_drivers WHERE role = 'offset' AND rnk = 1
)
SELECT
    'Forecast is ' || eur(t.curr_forecast) || ' (commit ' || eur(k.commit_total) || '), ' ||
    CASE
        WHEN t.total_change = 0 THEN 'flat vs last week.'
        ELSE CASE WHEN t.total_change < 0 THEN 'down ' ELSE 'up ' END ||
             eur(abs(t.total_change)) || ' vs last week, mainly because ' ||
             (SELECT txt FROM d) ||
             coalesce(', partly offset by ' || (SELECT txt FROM o), '') || '.'
    END AS headline,
    t.prev_forecast,
    t.curr_forecast,
    t.total_change,
    k.commit_total
FROM t, k;

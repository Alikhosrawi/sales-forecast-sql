-- Run parameters: everything else reads dates from this one table.
-- run_request(run_week) is written by run.py (the week the user asked for).
-- The quarter is always the quarter of the run week; last week's number is
-- re-evaluated against the SAME quarter so the two numbers are comparable.
CREATE OR REPLACE TABLE params AS
SELECT
    run_week,
    (run_week - 7)                                                   AS prev_week,
    run_week                                                         AS as_of,
    CAST(date_trunc('quarter', run_week) AS DATE)                    AS q_start,
    CAST(date_trunc('quarter', run_week) + INTERVAL 3 MONTH - INTERVAL 1 DAY AS DATE) AS q_end,
    strftime(run_week, '%G-W%V')                                     AS week_label,
    strftime(run_week - 7, '%G-W%V')                                 AS prev_week_label
FROM run_request;

-- Formatting helpers used by the report text.
CREATE OR REPLACE MACRO eur(x) AS
    CASE WHEN x < 0 THEN '−€' || format('{:,.0f}', -x) ELSE '€' || format('{:,.0f}', x) END;
CREATE OR REPLACE MACRO eur_signed(x) AS
    CASE WHEN x < 0 THEN '−€' || format('{:,.0f}', -x) ELSE '+€' || format('{:,.0f}', x) END;

-- check: dq_close_date_pushed_2x
-- severity: WARN
-- description: Open deals have not had their close date pushed out two or more times.
WITH moves AS (
    SELECT deal_id, snapshot_week, close_date,
           lag(close_date) OVER (PARTITION BY deal_id ORDER BY snapshot_week) AS prev_close
    FROM hist_mapped
)
SELECT 'dq_close_date_pushed_2x' AS check_id, 'WARN' AS severity, m.deal_id,
       'Close date pushed ' || count(*) || ' times' AS detail
FROM moves m
WHERE m.close_date > m.prev_close
  AND m.deal_id IN (SELECT deal_id FROM snap_raw
                    WHERE which = 'curr' AND stage NOT IN ('Closed Won', 'Closed Lost'))
GROUP BY m.deal_id
HAVING count(*) >= 2

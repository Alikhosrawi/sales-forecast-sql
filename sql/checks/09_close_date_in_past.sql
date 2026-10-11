-- check: dq_close_date_in_past
-- severity: WARN
-- description: Open deals do not have a close date that has already passed.
SELECT DISTINCT 'dq_close_date_in_past' AS check_id, 'WARN' AS severity, s.deal_id,
       'Still open but close date was ' || strftime(s.close_date, '%Y-%m-%d') ||
       ' (' || (p.as_of - s.close_date) || ' days ago)' AS detail
FROM snap_raw s, params p
WHERE s.which = 'curr'
  AND s.stage NOT IN ('Closed Won', 'Closed Lost')
  AND s.close_date < p.as_of

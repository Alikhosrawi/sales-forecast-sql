-- check: dq_stale_no_activity_21d
-- severity: WARN
-- description: Open deals have at least one logged activity in the last 21 days.
SELECT DISTINCT 'dq_stale_no_activity_21d' AS check_id, 'WARN' AS severity, s.deal_id,
       CASE WHEN la.last_activity_at IS NULL THEN 'No activity ever logged'
            ELSE 'No activity for ' || (p.as_of - la.last_activity_at) || ' days (last: ' ||
                 strftime(la.last_activity_at, '%Y-%m-%d') || ')' END AS detail
FROM snap_raw s
CROSS JOIN params p
JOIN deals d ON d.deal_id = s.deal_id
LEFT JOIN last_activity la ON la.deal_id = s.deal_id
WHERE s.which = 'curr'
  AND s.stage NOT IN ('Closed Won', 'Closed Lost')
  AND d.created_at <= p.as_of - 21
  AND (la.last_activity_at IS NULL OR la.last_activity_at < p.as_of - 21)

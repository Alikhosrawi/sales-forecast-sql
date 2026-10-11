# Data quality report, 2026-W33

Snapshot of 10 Aug 2026, compared with 03 Aug 2026. BLOCKER = the run stops, no forecast is produced. WARN = reported, fixed or flagged, run continues.

## Checks

| Check | Severity | Result | Rows | What it checks |
| :--- | :--- | :--- | ---: | :--- |
| dq_snapshot_missing | BLOCKER | PASS | 0 | A snapshot exists for this week and for last week (no snapshot = nothing to forecast or compare). |
| dq_missing_quota | BLOCKER | PASS | 0 | Every rep has a positive quarterly quota (attainment and gap are meaningless without it). |
| dq_unknown_stage_unmapped | BLOCKER | PASS | 0 | Every stage name is known or has a documented alias (otherwise there is no probability to apply). |
| dq_unknown_stage_mapped | WARN | WARN | 1 | Stage names match the current stage list (legacy names are translated via stage_aliases.csv). |
| dq_duplicate_deal | WARN | WARN | 1 | Each deal appears once in the CRM export and once per weekly snapshot. |
| dq_negative_amount | WARN | PASS | 0 | Deal amounts are not negative. |
| dq_missing_amount | WARN | WARN | 1 | Open deals have an amount. |
| dq_orphan_rep | WARN | WARN | 1 | Every deal owner exists in the reps table. |
| dq_close_date_in_past | WARN | PASS | 0 | Open deals do not have a close date that has already passed. |
| dq_stale_no_activity_21d | WARN | WARN | 11 | Open deals have at least one logged activity in the last 21 days. |
| dq_close_date_pushed_2x | WARN | WARN | 11 | Open deals have not had their close date pushed out two or more times. |

## Failing rows

### dq_unknown_stage_mapped (WARN)

- D0068: Stage "Solution design" is a legacy name; read as "Solution Design"

### dq_duplicate_deal (WARN)

- D0090: Deal appears 2 times in the CRM deals export

### dq_missing_amount (WARN)

- D0063: Open deal has no amount; counted as €0 until the rep fills it in

### dq_orphan_rep (WARN)

- D0039: Owner "R09" is not in the reps table; shown under Unassigned

### dq_stale_no_activity_21d (WARN)

- D0028: No activity for 179 days (last: 2026-02-12)
- D0039: No activity for 131 days (last: 2026-04-01)
- D0063: No activity for 113 days (last: 2026-04-19)
- D0070: No activity for 32 days (last: 2026-07-09)
- D0077: No activity for 44 days (last: 2026-06-27)
- D0078: No activity for 22 days (last: 2026-07-19)
- D0079: No activity for 43 days (last: 2026-06-28)
- D0085: No activity for 28 days (last: 2026-07-13)
- D0096: No activity for 24 days (last: 2026-07-17)
- D0097: No activity for 58 days (last: 2026-06-13)
- D0105: No activity for 31 days (last: 2026-07-10)

### dq_close_date_pushed_2x (WARN)

- D0028: Close date pushed 3 times
- D0036: Close date pushed 4 times
- D0037: Close date pushed 4 times
- D0039: Close date pushed 2 times
- D0046: Close date pushed 4 times
- D0055: Close date pushed 3 times
- D0063: Close date pushed 2 times
- D0070: Close date pushed 2 times
- D0072: Close date pushed 2 times
- D0073: Close date pushed 4 times
- D0098: Close date pushed 2 times

## Fixes applied (clean/ step)

Every automatic fix is logged here. Nothing is changed silently.

| Fix | Deal | Where | What was done |
| :--- | :--- | :--- | :--- |
| dedupe | D0090 | deals export | Removed 1 duplicate CRM record(s), kept one |
| missing_amount | D0063 | curr snapshot | Amount missing on an open deal: counted as €0 |
| orphan_rep | D0039 | deals export | Owner "R09" not found; moved to UNASSIGNED |
| stage_alias | D0068 | curr snapshot | Stage "Solution design" read as "Solution Design" |

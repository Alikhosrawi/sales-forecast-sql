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
| dq_close_date_in_past | WARN | WARN | 2 | Open deals do not have a close date that has already passed. |
| dq_stale_no_activity_21d | WARN | WARN | 4 | Open deals have at least one logged activity in the last 21 days. |
| dq_close_date_pushed_2x | WARN | WARN | 16 | Open deals have not had their close date pushed out two or more times. |

## Failing rows

### dq_unknown_stage_mapped (WARN)

- D0143: Stage "Qualified" is a legacy name; read as "Qualification"

### dq_duplicate_deal (WARN)

- D0149: Deal appears 2 times in the CRM deals export

### dq_missing_amount (WARN)

- D0129: Open deal has no amount; counted as €0 until the rep fills it in

### dq_orphan_rep (WARN)

- D0167: Owner "R09" is not in the reps table; shown under Unassigned

### dq_close_date_in_past (WARN)

- D0124: Still open but close date was 2026-07-30 (11 days ago)
- D0139: Still open but close date was 2026-08-03 (7 days ago)

### dq_stale_no_activity_21d (WARN)

- D0096: No activity for 115 days (last: 2026-04-17)
- D0122: No activity for 72 days (last: 2026-05-30)
- D0124: No activity for 73 days (last: 2026-05-29)
- D0143: No activity for 26 days (last: 2026-07-15)

### dq_close_date_pushed_2x (WARN)

- D0055: Close date pushed 6 times
- D0073: Close date pushed 5 times
- D0078: Close date pushed 4 times
- D0086: Close date pushed 4 times
- D0095: Close date pushed 2 times
- D0096: Close date pushed 2 times
- D0102: Close date pushed 4 times
- D0114: Close date pushed 3 times
- D0118: Close date pushed 2 times
- D0121: Close date pushed 2 times
- D0122: Close date pushed 3 times
- D0124: Close date pushed 2 times
- D0131: Close date pushed 3 times
- D0133: Close date pushed 3 times
- D0134: Close date pushed 3 times
- D0146: Close date pushed 2 times

## Fixes applied (clean/ step)

Every automatic fix is logged here. Nothing is changed silently.

| Fix | Deal | Where | What was done |
| :--- | :--- | :--- | :--- |
| dedupe | D0149 | deals export | Removed 1 duplicate CRM record(s), kept one |
| missing_amount | D0129 | curr snapshot | Amount missing on an open deal: counted as €0 |
| orphan_rep | D0167 | deals export | Owner "R09" not found; moved to UNASSIGNED |
| stage_alias | D0143 | curr snapshot | Stage "Qualified" read as "Qualification" |

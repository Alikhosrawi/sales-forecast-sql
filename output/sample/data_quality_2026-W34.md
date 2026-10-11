# Data quality report, 2026-W34

Snapshot of 17 Aug 2026, compared with 10 Aug 2026. BLOCKER = the run stops, no forecast is produced. WARN = reported, fixed or flagged, run continues.

## Checks

| Check | Severity | Result | Rows | What it checks |
| :--- | :--- | :--- | ---: | :--- |
| dq_snapshot_missing | BLOCKER | PASS | 0 | A snapshot exists for this week and for last week (no snapshot = nothing to forecast or compare). |
| dq_missing_quota | BLOCKER | PASS | 0 | Every rep has a positive quarterly quota (attainment and gap are meaningless without it). |
| dq_unknown_stage_unmapped | BLOCKER | PASS | 0 | Every stage name is known or has a documented alias (otherwise there is no probability to apply). |
| dq_unknown_stage_mapped | WARN | WARN | 2 | Stage names match the current stage list (legacy names are translated via stage_aliases.csv). |
| dq_duplicate_deal | WARN | WARN | 2 | Each deal appears once in the CRM export and once per weekly snapshot. |
| dq_negative_amount | WARN | WARN | 1 | Deal amounts are not negative. |
| dq_missing_amount | WARN | WARN | 1 | Open deals have an amount. |
| dq_orphan_rep | WARN | WARN | 1 | Every deal owner exists in the reps table. |
| dq_close_date_in_past | WARN | WARN | 1 | Open deals do not have a close date that has already passed. |
| dq_stale_no_activity_21d | WARN | WARN | 6 | Open deals have at least one logged activity in the last 21 days. |
| dq_close_date_pushed_2x | WARN | WARN | 17 | Open deals have not had their close date pushed out two or more times. |

## Failing rows

### dq_unknown_stage_mapped (WARN)

- D0121: Stage "Solution design" is a legacy name; read as "Solution Design"
- D0143: Stage "Qualified" is a legacy name; read as "Qualification"

### dq_duplicate_deal (WARN)

- D0149: Deal appears 2 times in the CRM deals export
- D0149: Deal appears 2 times in this week's snapshot

### dq_negative_amount (WARN)

- D0151: Amount is −€40,000; excluded from the forecast until fixed

### dq_missing_amount (WARN)

- D0129: Open deal has no amount; counted as €0 until the rep fills it in

### dq_orphan_rep (WARN)

- D0167: Owner "R09" is not in the reps table; shown under Unassigned

### dq_close_date_in_past (WARN)

- D0118: Still open but close date was 2026-08-08 (9 days ago)

### dq_stale_no_activity_21d (WARN)

- D0055: No activity for 23 days (last: 2026-07-25)
- D0096: No activity for 122 days (last: 2026-04-17)
- D0122: No activity for 79 days (last: 2026-05-30)
- D0124: No activity for 80 days (last: 2026-05-29)
- D0143: No activity for 33 days (last: 2026-07-15)
- D0158: No activity for 27 days (last: 2026-07-21)

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
- D0124: Close date pushed 3 times
- D0131: Close date pushed 3 times
- D0133: Close date pushed 3 times
- D0134: Close date pushed 3 times
- D0135: Close date pushed 2 times
- D0146: Close date pushed 3 times

## Fixes applied (clean/ step)

Every automatic fix is logged here. Nothing is changed silently.

| Fix | Deal | Where | What was done |
| :--- | :--- | :--- | :--- |
| dedupe | D0149 | curr snapshot | Removed 1 duplicate snapshot row(s), kept one |
| dedupe | D0149 | deals export | Removed 1 duplicate CRM record(s), kept one |
| missing_amount | D0129 | curr snapshot | Amount missing on an open deal: counted as €0 |
| missing_amount | D0129 | prev snapshot | Amount missing on an open deal: counted as €0 |
| negative_amount | D0151 | curr snapshot | Amount −€40,000: deal excluded from the forecast |
| orphan_rep | D0167 | deals export | Owner "R09" not found; moved to UNASSIGNED |
| stage_alias | D0121 | curr snapshot | Stage "Solution design" read as "Solution Design" |
| stage_alias | D0143 | curr snapshot | Stage "Qualified" read as "Qualification" |
| stage_alias | D0143 | prev snapshot | Stage "Qualified" read as "Qualification" |

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
| dq_close_date_in_past | WARN | WARN | 2 | Open deals do not have a close date that has already passed. |
| dq_stale_no_activity_21d | WARN | WARN | 13 | Open deals have at least one logged activity in the last 21 days. |
| dq_close_date_pushed_2x | WARN | WARN | 14 | Open deals have not had their close date pushed out two or more times. |

## Failing rows

### dq_unknown_stage_mapped (WARN)

- D0068: Stage "Proposal Sent" is a legacy name; read as "Proposal"
- D0087: Stage "Proposal Sent" is a legacy name; read as "Proposal"

### dq_duplicate_deal (WARN)

- D0090: Deal appears 2 times in the CRM deals export
- D0090: Deal appears 2 times in this week's snapshot

### dq_negative_amount (WARN)

- D0099: Amount is −€37,500; excluded from the forecast until fixed

### dq_missing_amount (WARN)

- D0063: Open deal has no amount; counted as €0 until the rep fills it in

### dq_orphan_rep (WARN)

- D0039: Owner "R09" is not in the reps table; shown under Unassigned

### dq_close_date_in_past (WARN)

- D0067: Still open but close date was 2026-08-10 (7 days ago)
- D0098: Still open but close date was 2026-08-08 (9 days ago)

### dq_stale_no_activity_21d (WARN)

- D0028: No activity for 186 days (last: 2026-02-12)
- D0039: No activity for 138 days (last: 2026-04-01)
- D0063: No activity for 120 days (last: 2026-04-19)
- D0068: No activity for 22 days (last: 2026-07-26)
- D0077: No activity for 51 days (last: 2026-06-27)
- D0078: No activity for 29 days (last: 2026-07-19)
- D0079: No activity for 50 days (last: 2026-06-28)
- D0087: No activity for 24 days (last: 2026-07-24)
- D0096: No activity for 31 days (last: 2026-07-17)
- D0097: No activity for 65 days (last: 2026-06-13)
- D0104: No activity for 27 days (last: 2026-07-21)
- D0105: No activity for 38 days (last: 2026-07-10)
- D0120: No activity for 23 days (last: 2026-07-25)

### dq_close_date_pushed_2x (WARN)

- D0028: Close date pushed 3 times
- D0036: Close date pushed 4 times
- D0037: Close date pushed 4 times
- D0039: Close date pushed 2 times
- D0046: Close date pushed 4 times
- D0055: Close date pushed 3 times
- D0063: Close date pushed 2 times
- D0069: Close date pushed 2 times
- D0070: Close date pushed 2 times
- D0073: Close date pushed 4 times
- D0079: Close date pushed 2 times
- D0098: Close date pushed 2 times
- D0104: Close date pushed 2 times
- D0109: Close date pushed 2 times

## Fixes applied (clean/ step)

Every automatic fix is logged here. Nothing is changed silently.

| Fix | Deal | Where | What was done |
| :--- | :--- | :--- | :--- |
| dedupe | D0090 | curr snapshot | Removed 1 duplicate snapshot row(s), kept one |
| dedupe | D0090 | deals export | Removed 1 duplicate CRM record(s), kept one |
| missing_amount | D0063 | curr snapshot | Amount missing on an open deal: counted as €0 |
| missing_amount | D0063 | prev snapshot | Amount missing on an open deal: counted as €0 |
| negative_amount | D0099 | curr snapshot | Amount −€37,500: deal excluded from the forecast |
| orphan_rep | D0039 | deals export | Owner "R09" not found; moved to UNASSIGNED |
| stage_alias | D0068 | curr snapshot | Stage "Proposal Sent" read as "Proposal" |
| stage_alias | D0068 | prev snapshot | Stage "Solution design" read as "Solution Design" |
| stage_alias | D0087 | curr snapshot | Stage "Proposal Sent" read as "Proposal" |

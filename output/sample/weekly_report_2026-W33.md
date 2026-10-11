# Weekly forecast: Fernbrook Analytics, 2026-W33

_Q3 2026 (01 Jul – 30 Sep 2026) · snapshot of 10 Aug 2026 · compared with 2026-W32 · all data is synthetic and fictional_

> **Forecast is €921,166 (commit €460,500), down €85,552 vs last week, mainly because 4 deals were lost (−€69,813; biggest: Lotsenhaus – Seat expansion) and 1 deal slipped out of the quarter (−€16,169), partly offset by stage moves (+€15,967 across 3 deals).**

## The numbers

|  | This week | Last week | Change |
| :--- | ---: | ---: | ---: |
| Forecast (closed won + weighted open) | €921,166 | €1,006,718 | −€85,552 |

| Measure | Amount | What it means |
| :--- | ---: | :--- |
| Quota | €1,330,000 | Sum of rep quotas for the quarter |
| Closed won | €344,500 | Attainment to date: 25.9% |
| Gap to quota | €985,500 | Still needed from open deals |
| Commit | €460,500 | Closed won + open deals reps marked commit |
| Best case | €999,500 | Commit + open deals marked best case |
| Open pipeline (unweighted) | €1,098,500 | 30 open deals due to close this quarter |
| Forecast (weighted) | €921,166 | 69.3% of quota |

## Why it moved: the bridge

![Forecast bridge](charts/bridge_2026-W33.png)

| Amount | Bucket | Deals |
| ---: | :--- | :--- |
| €1,006,718 | Last week's forecast |  |
| −€69,813 | Lost | 4 (biggest: Lotsenhaus – Seat expansion) |
| −€16,169 | Slipped out of the quarter | 1 (Grünspan – Pipeline analytics pilot) |
| −€15,536 | Amount decreased | 3 (biggest: Ilmenau – Forecasting module) |
| +€15,967 | Stage moves | 3 (biggest: Kranichfeld – Data quality audit) |
| €921,166 | **This week's forecast** |  |

Buckets add up to the total change exactly: −€85,552 = €921,166 − €1,006,718 (unexplained: €0.00).

## Top 5 deals at risk

28 open deals have at least one warning sign. These five count toward this quarter and have the most signs, then the most money at stake.

| # | Deal | Owner | Stage | Amount | Close | Why it is at risk |
| ---: | :--- | :--- | :--- | ---: | :--- | :--- |
| 1 | Lotsenhaus – Reporting automation | Mira Okonkwo | Discovery | €161,000 | 10 Sep | Close date pushed 4 times (first 25 May, now 10 Sep); Moved back from Solution Design to Discovery (week of 03 Aug); Due to close 10 Sep but still in Discovery |
| 2 | Ilmenau – Forecasting module | Jonas Brenner | Discovery | €51,500 | 21 Aug | Close date pushed 3 times (first 04 Jun, now 21 Aug); No activity for 72 days; Due to close 21 Aug but still in Discovery |
| 3 | Ilmenau – Forecasting module | Mira Okonkwo | Negotiation | €23,000 | 25 Aug | Close date pushed 6 times (first 29 Mar, now 25 Aug); No activity for 16 days; Amount cut 40% (from €38,500 to €23,000) |
| 4 | Grünspan – Data quality audit | Lena Hartwig | Solution Design | €47,500 | 30 Aug | Close date pushed 2 times (first 25 Jun, now 30 Aug); Moved back from Solution Design to Discovery (week of 13 Jul) |
| 5 | Wellenbrecher – Data quality audit | Jonas Brenner | Solution Design | €36,500 | 31 Aug | Close date pushed 2 times (first 06 Jul, now 31 Aug); No activity for 115 days |

## Forecast vs quota by rep

![Forecast vs quota](charts/forecast_vs_quota_2026-W33.png)

| Rep | Team | Quota | Closed won | Attainment | Commit | Best case | Forecast | Gap to quota |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mira Okonkwo | Enterprise | €420,000 | €52,000 | 12.4% | €168,000 | €228,500 | €246,164 | €368,000 |
| Tobias Lindvall | Enterprise | €400,000 | €269,500 | 67.4% | €269,500 | €385,500 | €351,535 | €130,500 |
| Lena Hartwig | Mid-Market | €260,000 | €0 | 0.0% | €0 | €81,000 | €74,070 | €260,000 |
| Jonas Brenner | Mid-Market | €250,000 | €23,000 | 9.2% | €23,000 | €304,500 | €233,850 | €227,000 |
| Unassigned | Unassigned | – | €0 | – | €0 | €0 | €15,548 | – |

## Data issues found this run

4 of 11 checks passed; 7 raised warnings, none blocked the run. Full detail: [data_quality_2026-W33.md](data_quality_2026-W33.md)

- **dq_unknown_stage_mapped**: 1 row(s). Stage names match the current stage list (legacy names are translated via stage_aliases.csv).
- **dq_duplicate_deal**: 1 row(s). Each deal appears once in the CRM export and once per weekly snapshot.
- **dq_missing_amount**: 1 row(s). Open deals have an amount.
- **dq_orphan_rep**: 1 row(s). Every deal owner exists in the reps table.
- **dq_close_date_in_past**: 2 row(s). Open deals do not have a close date that has already passed.
- **dq_stale_no_activity_21d**: 4 row(s). Open deals have at least one logged activity in the last 21 days.
- **dq_close_date_pushed_2x**: 16 row(s). Open deals have not had their close date pushed out two or more times.

## Backtest

Backtest, week-6 forecast versus actual closed won: Q1 2026 as of 2026-W07 error +16.8% (+€80,200.00); Q2 2026 as of 2026-W20 error +7.1% (+€91,899.10).

Full quarter-by-quarter figures: [backtest.md](backtest.md).

## How deals were weighted

| Stage | Probability used | Source | Default |
| :--- | ---: | :--- | :--- |
| Qualification | 27% | historical win rate (n=88) | 10% |
| Discovery | 41% | historical win rate (n=82) | 20% |
| Solution Design | 56% | historical win rate (n=61) | 40% |
| Proposal | 71% | historical win rate (n=48) | 60% |
| Negotiation | 81% | historical win rate (n=42) | 80% |

Historical win rate = share of deals that reached the stage and were won, among deals closed before this quarter. Used when at least 10 such deals exist, otherwise the default. See [docs/methodology.md](../docs/methodology.md).

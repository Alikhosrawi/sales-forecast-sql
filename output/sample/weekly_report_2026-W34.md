# Weekly forecast: Fernbrook Analytics, 2026-W34

_Q3 2026 (01 Jul – 30 Sep 2026) · snapshot of 17 Aug 2026 · compared with 2026-W33 · all data is synthetic and fictional_

> **Forecast is €1,316,387 (commit €793,000), down €84,547 vs last week, mainly because 1 deal slipped out of the quarter (−€94,500: Lotsenhaus – Forecasting module) and 5 deals were lost (−€55,559), partly offset by stage moves (+€56,927 across 9 deals).**

## The numbers

|  | This week | Last week | Change |
| :--- | ---: | ---: | ---: |
| Forecast (closed won + weighted open) | €1,316,387 | €1,400,934 | −€84,547 |

| Measure | Amount | What it means |
| :--- | ---: | :--- |
| Quota | €1,330,000 | Sum of rep quotas for the quarter |
| Closed won | €571,000 | Attainment to date: 42.9% |
| Gap to quota | €759,000 | Still needed from open deals |
| Commit | €793,000 | Closed won + open deals reps marked commit |
| Best case | €1,135,500 | Commit + open deals marked best case |
| Open pipeline (unweighted) | €1,809,500 | 29 open deals due to close this quarter |
| Forecast (weighted) | €1,316,387 | 99.0% of quota |

## Why it moved: the bridge

![Forecast bridge](charts/bridge_2026-W34.png)

| Amount | Bucket | Deals |
| ---: | :--- | :--- |
| €1,400,934 | Last week's forecast |  |
| +€12,691 | Pulled into the quarter | 1 (Dünenweg – Revenue Dashboard rollout) |
| +€12,000 | Won (moved to 100%) | 1 (Uferlicht – Seat expansion) |
| −€55,559 | Lost | 5 (biggest: Brückenhof – Reporting automation) |
| −€94,500 | Slipped out of the quarter | 1 (Lotsenhaus – Forecasting module) |
| +€1,200 | Amount increased | 1 (Elbwiese – Reporting automation) |
| +€56,927 | Stage moves | 9 (biggest: Brückenhof – Data quality audit) |
| −€17,306 | Excluded/restored by data checks | 1 (Grünspan – Pipeline analytics pilot) |
| €1,316,387 | **This week's forecast** |  |

Buckets add up to the total change exactly: −€84,547 = €1,316,387 − €1,400,934 (unexplained: €0.00).

## Top 5 deals at risk

32 open deals have at least one warning sign. These five count toward this quarter and have the most signs, then the most money at stake.

| # | Deal | Owner | Stage | Amount | Close | Why it is at risk |
| ---: | :--- | :--- | :--- | ---: | :--- | :--- |
| 1 | Pfefferland – Data quality audit | Mira Okonkwo | Qualification | €90,000 | 27 Sep | No activity for 51 days; Moved back from Discovery to Qualification (week of 10 Aug); Due to close 27 Sep but still in Qualification |
| 2 | Ilmenau – Seat expansion | Tobias Lindvall | Qualification | €60,000 | 03 Sep | No activity for 29 days; Amount cut 30% (from €86,000 to €60,000); Due to close 03 Sep but still in Qualification |
| 3 | Lotsenhaus – Revenue Dashboard rollout | Mira Okonkwo | Qualification | €55,000 | 03 Sep | Moved back from Discovery to Qualification (week of 17 Aug); Amount cut 30% (from €78,500 to €55,000); Due to close 03 Sep but still in Qualification |
| 4 | Lotsenhaus – Seat expansion | Lena Hartwig | Discovery | €0 | 25 Aug | Close date pushed 2 times (first 04 Aug, now 25 Aug); No activity for 120 days; Due to close 25 Aug but still in Discovery |
| 5 | Tidenhub – Seat expansion | Mira Okonkwo | Proposal | €57,500 | 04 Sep | Close date pushed 4 times (first 30 May, now 04 Sep); Amount cut 30% (from €82,500 to €57,500) |

## Forecast vs quota by rep

![Forecast vs quota](charts/forecast_vs_quota_2026-W34.png)

| Rep | Team | Quota | Closed won | Attainment | Commit | Best case | Forecast | Gap to quota |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mira Okonkwo | Enterprise | €420,000 | €203,500 | 48.5% | €269,000 | €393,500 | €429,631 | €216,500 |
| Tobias Lindvall | Enterprise | €400,000 | €96,000 | 24.0% | €165,000 | €330,000 | €410,590 | €304,000 |
| Lena Hartwig | Mid-Market | €260,000 | €0 | 0.0% | €40,000 | €74,000 | €141,764 | €260,000 |
| Jonas Brenner | Mid-Market | €250,000 | €271,500 | 108.6% | €313,500 | €332,500 | €331,101 | €0 (over by €21,500) |
| Unassigned | Unassigned | – | €0 | – | €5,500 | €5,500 | €3,300 | – |

## Data issues found this run

3 of 11 checks passed; 8 raised warnings, none blocked the run. Full detail: [data_quality_2026-W34.md](data_quality_2026-W34.md)

- **dq_unknown_stage_mapped**: 2 row(s). Stage names match the current stage list (legacy names are translated via stage_aliases.csv).
- **dq_duplicate_deal**: 2 row(s). Each deal appears once in the CRM export and once per weekly snapshot.
- **dq_negative_amount**: 1 row(s). Deal amounts are not negative.
- **dq_missing_amount**: 1 row(s). Open deals have an amount.
- **dq_orphan_rep**: 1 row(s). Every deal owner exists in the reps table.
- **dq_close_date_in_past**: 2 row(s). Open deals do not have a close date that has already passed.
- **dq_stale_no_activity_21d**: 13 row(s). Open deals have at least one logged activity in the last 21 days.
- **dq_close_date_pushed_2x**: 14 row(s). Open deals have not had their close date pushed out two or more times.

## Backtest

Backtest, week-6 forecast versus actual closed won: Q1 2026 as of 2026-W07 error +€49,600.00 (percent not defined, actual closed won €0.00); Q2 2026 as of 2026-W20 error +16.8% (+€80,200.00).

Full quarter-by-quarter figures: [backtest.md](backtest.md).

## How deals were weighted

| Stage | Probability used | Source | Default |
| :--- | ---: | :--- | :--- |
| Qualification | 23% | historical win rate (n=44) | 10% |
| Discovery | 32% | historical win rate (n=37) | 20% |
| Solution Design | 46% | historical win rate (n=26) | 40% |
| Proposal | 60% | historical win rate (n=20) | 60% |
| Negotiation | 75% | historical win rate (n=16) | 80% |

Historical win rate = share of deals that reached the stage and were won, among deals closed before this quarter. Used when at least 10 such deals exist, otherwise the default. See [docs/methodology.md](../docs/methodology.md).

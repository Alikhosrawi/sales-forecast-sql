# Methodology

How the number is built, and how the week-over-week bridge explains it. Every rule here lives in a `.sql` file; the file is named next to each rule.

## 1. Which deals count

The forecast is always for **the quarter of the run week** (Q3 2026 for the sample week, 17 Aug 2026). A deal counts if its close date falls inside that quarter. Last week's number is recalculated against the same quarter, so the two numbers are comparable even in the first week of a new quarter. (`sql/staging/00_params.sql`)

## 2. Stage probabilities (`sql/forecast/01_stage_probability.sql`)

For each stage, the pipeline looks at deals that **closed before the quarter started** and asks: of the deals that were ever in this stage, what share was won?

| Rule | Probability used |
|---|---|
| 10 or more such deals | their historical win rate, rounded to 4 decimals |
| fewer than 10 | the default probability from the `stages` table |
| Closed Won / Closed Lost | 100% / 0% |

The report prints which source each stage used and how many deals it was based on. Using only pre-quarter history keeps the probabilities fixed for every week of the quarter, so a change in the forecast is always a change in the deals, never a change in the method.

Simplifications: a deal "reached" a stage only if a weekly snapshot caught it there, so a deal that jumped two stages in one week does not count for the stage in between. Win rates are company-wide, not per rep or per deal size.

## 3. The forecast (`sql/forecast/02_deal_values.sql` to `04_team_forecast.sql`)

Each deal contributes:

- **won, closing this quarter**: its full amount
- **open, closing this quarter**: amount × stage probability, rounded to the cent
- **anything else**: 0

**Forecast = closed won + weighted open pipeline.** Next to it the report shows the numbers a sales leader is used to, based on the forecast category reps set on each deal (not weighted):

- **Commit** = closed won + open deals marked `commit`
- **Best case** = commit + open deals marked `best_case`
- **Pipeline** = open deals marked `pipeline`
- **Attainment** = closed won ÷ quota; **gap to quota** = quota − closed won

## 4. Data quality before every run (`sql/checks/`, `sql/clean/`)

Each check is one SQL file that returns the rows that fail, with a severity:

- **BLOCKER**: the run stops and no forecast is written (no snapshot for the week, a rep without quota, a stage name nobody can translate).
- **WARN**: the issue is reported, and where there is a safe fix it is applied and logged in `clean_log`:

| Issue | Fix |
|---|---|
| duplicate deal rows | keep one (the larger amount if they disagree) |
| legacy stage name (e.g. "Proposal Sent") | translate via `data/seeds/stage_aliases.csv` |
| owner not in the reps table | keep the deal under "Unassigned" (counts for the total, no rep quota) |
| negative amount | leave the deal out until fixed (could be a typo or a credit note) |
| missing amount on an open deal | count it as €0 |
| close date in the past, no activity 21+ days, close date pushed 2+ times | reported only; a person has to look |

## 5. The bridge (`sql/bridge/`)

The bridge explains `this week's forecast − last week's forecast`, deal by deal. Each deal's change goes into exactly one bucket, checked in this order:

1. Not in last week's (clean) snapshot → **new** (or **data checks**, if it was in the raw data but excluded last week)
2. Not in this week's (clean) snapshot → **other** (deleted) (or **data checks**, if it was excluded this week)
3. Open → won → **won** (the jump from its weighted value to 100%)
4. Open → lost → **lost**
5. Open both weeks, close date moved out of the quarter → **slipped**; moved in → **pulled in**
6. Open both weeks and in the quarter → split in two:
   - **amount effect** = (new amount − old amount) × last week's probability → **amount up / amount down**
   - **stage effect** = the rest of the change → **stage moves**
   (If the stage did not change, the whole change is the amount effect.)
7. Anything else (e.g. a reopened deal) → **other**

Because the stage effect is defined as "the rest", the two parts of a deal always add up to that deal's change, to the cent. And because every deal's change lands somewhere, **the buckets add up to the total change exactly**. `tests/test_bridge.py` checks this for every week of the quarter, and also checks each deal individually.

The order matters only for deals where two things happened at once (for example a deal pulled into the quarter that also changed stage counts fully as "pulled in"). This is a deliberate choice: one clear reason per deal is easier to act on than a perfect split.

## 6. The headline (`sql/report/01_headline.sql`)

The sentence is built from the bridge: the two largest buckets that moved in the same direction as the total are the "mainly because", and the largest bucket in the other direction is the "partly offset by". For the biggest driver, the deal name is added so the reader knows where to look first.

## 7. Risk flags (`sql/risk/`)

For every open deal, five signals, each with its own sentence:

| Flag | Rule |
|---|---|
| close date pushed 2+ times | close date moved later in two or more weekly snapshots |
| no activity 14+ days | no call, email, meeting or demo logged in 14 days |
| stage moved backwards | a lower stage than the week before, during this quarter |
| amount cut 20%+ | current amount ≤ 80% of its highest amount this quarter |
| early stage, closing this quarter | in Qualification or Discovery but due to close this quarter |

The top 5 in the report are deals that count toward this quarter, ranked by number of flags, then by weighted value.

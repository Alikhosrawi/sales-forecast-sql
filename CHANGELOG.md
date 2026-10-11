# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Changes to the *numbers* are tracked separately, run by run, in `output/run_log.csv`.

## [Unreleased]

## [0.1.0] - 2026-10-11

### Added
- Synthetic CRM generator for the fictional Fernbrook Analytics (seed 42): reps, accounts, deals,
  weekly deal snapshots, activities, stages, with documented data problems listed in `injected_issues.json`.
- 11 data-quality checks in SQL (3 BLOCKER, 8 WARN) and a data-quality report per run.
- Cleaning step with logged fixes: dedupe, stage-name aliases, unassigned owners, invalid amounts.
- Quarter forecast: stage probabilities from historical win rates (n ≥ 10) or defaults; commit, best case,
  pipeline, attainment and gap to quota by rep and team.
- Five risk flags per open deal with a plain-English reason; top 5 at-risk deals in the report.
- Week-over-week forecast bridge with ten buckets that sum exactly to the total change.
- Weekly Markdown report with an auto-written headline, waterfall and forecast-vs-quota charts.
- `output/run_log.csv` audit trail (timestamp, data week, checks, forecast, change, git commit).
- pytest suite (34 tests) and GitHub Actions CI.
- README, methodology, MIT licence.

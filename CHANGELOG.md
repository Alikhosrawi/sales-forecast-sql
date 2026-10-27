# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Changes to the *numbers* are tracked separately, run by run, in `output/run_log.csv`.

## [Unreleased]

### Changed
- The fictional industry label is Consumer Goods. Its German account-name suffix is Handel.

### Fixed
- Sample history starts on Monday 6 Oct 2025. Starting on 5 Jan 2026 meant no deal could be closed won inside Q1 2026, so the Q1 percent error was undefined. Both backtest quarters now have a closed-won total and a defined percent and EUR error. The errors that fell out were not tuned, and the sample week of 17 Aug 2026 was regenerated from the same seed.

## [0.2.0] - 2026-10-11

### Added
- Quarter backtest (`sql/backtest/`): week 6 of each of the two previous quarters versus actual closed won, in EUR and percent, written to `output/backtest.md` and quoted in the weekly report.
- `scripts/leak_scan.sh`, wired into GitHub Actions. The word list is read from a gitignored local file or from the `LEAK_WORDS` Actions secret. If neither is set, the step warns and checks credential assignments only.
- A pytest that runs the backtest and checks the output file against the run.

### Changed
- The fictional company name is Fernbrook Analytics.
- One industry label and two account-name stems were renamed so the sample stays fictional and clear of the word list.
- Letter-only word-list hits must be whole tokens, so the standard licence text is not flagged.

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

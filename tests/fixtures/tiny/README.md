# Tiny fixture

Five hand-made deals, one rep, two weekly snapshots (2026-W33 and 2026-W34).
No deals closed before Q3, so every stage uses its default probability.

Expected values, worked out by hand (also in tests/test_forecast.py):

| Deal | This week | Value this week | Last week | Value last week | Bridge bucket |
|---|---|---:|---|---:|---|
| T1 | Negotiation, €10,000, Sep 10 | 10,000 × 0.80 = 8,000.00 | Proposal | 10,000 × 0.60 = 6,000.00 | stage move +2,000.00 |
| T2 | Proposal, €20,000, Sep 20 | 20,000 × 0.60 = 12,000.00 | same | 12,000.00 | no change |
| T3 | Closed Won, €5,000 | 5,000.00 | Negotiation | 5,000 × 0.80 = 4,000.00 | won +1,000.00 |
| T4 | Discovery, close Oct 15 (Q4) | 0.00 | Discovery, close Sep 25 | 7,000 × 0.20 = 1,400.00 | slipped −1,400.00 |
| T5 | Qualification, €3,333 | 3,333 × 0.10 = 333.30 | (did not exist) | 0.00 | new +333.30 |
| **Total** | | **25,333.30** | | **23,400.00** | **+1,933.30** |

Commit = closed won 5,000 + open commit (T1) 10,000 = 15,000.

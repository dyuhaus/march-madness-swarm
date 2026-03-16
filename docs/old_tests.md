# Experiment Log

All attempted changes to `predict.py` are logged here. Agents MUST review this before proposing new changes. **Do not make duplicate changes.**

Format for each entry:
```
## Experiment #N — [PASS/FAIL]
- Agent: agent-N
- Date: YYYY-MM-DD HH:MM
- Baseline Score: X.X
- New Score: X.X (change: +/-X.X)
- Change: Brief description
- Details: What was modified and why
- Per-Year Breakdown:
  - 2022: X → Y
  - 2023: X → Y
  - 2024: X → Y
  - 2025: X → Y
- Analysis: What improved, what declined, and why
```

---

## Experiment #0 — BASELINE (CORRECTED)
- Agent: setup (manual)
- Date: 2026-03-16
- Baseline Score: N/A (this IS the baseline)
- New Score: 970.0
- Change: Seed-based algorithm with stat adjustments + cascading bracket predictions
- Details: Fixed predict_bracket to chain own predictions for later rounds instead of reading actual matchups from bracket data (which was inflating scores). Fixed team name mismatches (LSU, USC, BYU, VCU, Ole Miss, Loyola Chicago) so stats are properly used for all tournament teams.
- Per-Year Breakdown:
  - 2022: 940 (37/63 correct, 49.0%)
  - 2023: 580 (40/63 correct, 30.2%)
  - 2024: 1240 (42/63 correct, 64.6%)
  - 2025: 1120 (50/63 correct, 58.3%)
- Analysis: R64 accuracy 69-81%. Cascading errors hurt later rounds significantly. 2023 worst year (upset-heavy: 16-seed FDU beat 1-seed Purdue, 4-seed UConn won it all). 2024 best (1-seed UConn repeated). Key areas to improve: upset detection, stat-based adjustments, late-round weighting.


## Experiment #3 — FAIL
- Agent: agent-1
- Date: 2026-03-16 11:45
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm increasing the seed decay more aggressively in later rounds to make upset predictions more likely in the Final Four and Championship games. The current decay only reduces seed advantage to 60% and 55% in the final rounds, but historically, lower seeds have better chances in later rounds when they've already proven themselves by advancing. This should help capture more upsets in high-value rounds.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Tested aggressive seed decay in Final Four (0.60→0.40) and Championship (0.55→0.30) rounds to increase upset likelihood in the highest-value games. This makes the algorithm more willing to pick lower seeds that have proven themselves by advancing deep into the tournament, which could capture historical patterns where teams like UConn (4-seed in 2023) or other lower seeds win championships.


## Experiment #4 — FAIL
- Agent: agent-2
- Date: 2026-03-16 11:45
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm reducing the championship game seed decay from 0.55 to 0.75 to make the algorithm more conservative about picking upsets in the final game. The championship is worth 320 points (1/6 of total bracket), and historically 1-2 seeds win about 70% of championships. The current decay makes the algorithm too willing to pick lower seeds that have advanced, but championship games typically favor the higher seeds more than our current model suggests.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Championship game seed decay should be higher (more conservative) than Final Four decay. The championship is the single highest-value game (320 points) and historically favors higher seeds more than our previous setting suggested. A decay of 0.75 vs 0.55 means seed advantages are preserved more in the final, which should align better with historical championship patterns where 1-2 seeds win about 70% of the time.


## Experiment #5 — FAIL
- Agent: agent-3
- Date: 2026-03-16 11:46
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm reducing the decay factor for early rounds (Round of 64 and Round of 32) from 1.0/0.90 to 0.95/0.85 to make the algorithm slightly more willing to pick upsets in the first two rounds. This should help capture some of the 12-over-5 and 11-over-6 upsets that happen frequently (~35-37%) while maintaining seed advantages in later rounds where they matter more for scoring.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Early round decay adjustment tested - reducing Round of 64 decay from 1.0 to 0.95 and Round of 32 decay from 0.90 to 0.85 makes the algorithm more willing to pick upsets in the first two rounds where common upset patterns (12-over-5, 11-over-6) occur frequently. This targets the historical ~35-37% upset rates in these matchups while preserving seed advantages in later rounds where they're more important for scoring.

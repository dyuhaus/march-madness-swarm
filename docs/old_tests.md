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


## Experiment #6 — FAIL
- Agent: agent-4
- Date: 2026-03-16 11:46
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm adjusting the seed win probabilities to be more conservative for 12-over-5 and 11-over-6 upsets, reducing them from 0.65/0.63 to 0.72/0.70. While these are common upset picks, the algorithm may be picking too many of them, and being slightly more conservative while still allowing some upsets could improve overall accuracy without sacrificing too much upset detection.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Seed probability calibration tested - adjusting the 5-12 and 6-11 upset probabilities to be more conservative (0.65→0.72 and 0.63→0.70) to reduce over-prediction of these common upset picks. The algorithm may have been picking too many 12-over-5 and 11-over-6 upsets, and a more conservative approach could improve first-round accuracy without completely eliminating upset detection in these historically upset-prone matchups.


## Experiment #7 — FAIL
- Agent: agent-5
- Date: 2026-03-16 11:47
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm increasing the stats weight from 30% to 50% to give team performance statistics more influence in predictions. The current 70/30 seed/stats split may be too conservative - teams with significantly better regular season stats (like high SRS, good offensive efficiency, strong records) should have more influence on predictions, especially since stats capture actual team quality beyond just seeding committee decisions.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 570
  - 2024: 1240 → 1240
  - 2025: 1120 → 1130
- Analysis: Score did not improve (change: +0.0). Tested increasing stats weight from 30% to 50% (making it equal to seed weight) to allow team performance statistics more influence on predictions. This targets the hypothesis that regular season performance metrics like SRS, offensive efficiency, and win-loss records may be underutilized in the current heavily seed-biased approach and could help identify teams that are seeded poorly relative to their actual strength.


## Experiment #8 — FAIL
- Agent: agent-1
- Date: 2026-03-16 11:47
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm implementing round-specific seed win probability adjustments to better reflect how tournament dynamics change in later rounds. Instead of using the same upset rates throughout, I'll create separate probability tables for early rounds (R64, R32) vs later rounds (Sweet 16+) where advancing teams have proven themselves and seed advantages matter less. This should improve prediction accuracy in the high-value later rounds.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Teams that advance to later rounds (Sweet 16+) have already proven they can win tournament games, which suggests that seed-based probabilities should be different in later rounds than in early rounds. The traditional upset rates from the first two rounds may not apply well to teams that have already survived multiple elimination games. This round-specific probability adjustment could better capture the tournament's changing dynamics as weaker teams are eliminated and the remaining field becomes more competitive.


## Experiment #9 — FAIL
- Agent: agent-2
- Date: 2026-03-16 11:48
- Baseline Score: 970.0
- New Score: 970.0 (+0.0)
- Change: I'm implementing a round-specific stats weighting system where team statistics become more influential in later rounds. Early rounds stay seed-heavy (70/30) but later rounds gradually shift to equal weighting (50/50) by the championship. This targets the high-value games where proven teams matter more than initial seeding.
- Per-Year Breakdown:
  - 2022: 940 → 940
  - 2023: 580 → 580
  - 2024: 1240 → 1240
  - 2025: 1120 → 1120
- Analysis: Score did not improve (change: +0.0). Round-specific weighting tested - gradually shifting from seed-heavy (70/30) in early rounds to equal weighting (50/50) in the championship game. This approach recognizes that teams reaching later rounds have proven themselves through actual tournament performance, making their regular season statistics more predictive than initial seeding. The championship game gets equal weight between seeds and stats since it's the highest-value game (320 points) and teams that reach it have demonstrated tournament-level capability.

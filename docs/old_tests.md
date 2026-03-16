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

## Experiment #0 — BASELINE
- Agent: setup (manual)
- Date: 2026-03-16
- Baseline Score: N/A (this IS the baseline)
- New Score: 1495.0
- Change: Initial seed-based algorithm with stat adjustments
- Details: Seed win probabilities + round decay + SRS/SOS/off_rtg stat factors
- Per-Year Breakdown:
  - 2022: 1420 (45/63 correct, 74.0%)
  - 2023: 1400 (47/63 correct, 72.9%)
  - 2024: 1530 (47/63 correct, 79.7%)
  - 2025: 1630 (52/63 correct, 84.9%)
- Analysis: Strong late-round performance (seed advantage dominates). Weakest in early rounds where upsets are common. 2025 had all #1 seeds in Final Four, inflating that year's score. Room to improve upset detection and stat utilization.

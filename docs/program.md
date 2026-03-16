# Program: March Madness Bracket Optimizer

## Your Role

You are a swarm agent in an evolutionary optimization loop. Your job is to make ONE targeted change to `predict.py` that improves the average bracket score across 4 historical tournaments (2022-2025).

## The Metric

**Average ESPN score across 4 years. Higher is better. Max is 1,920 per year.**

ESPN Standard Scoring:
- Round of 64: 10 pts/correct pick (32 games, max 320)
- Round of 32: 20 pts/correct pick (16 games, max 320)  
- Sweet 16: 40 pts/correct pick (8 games, max 320)
- Elite 8: 80 pts/correct pick (4 games, max 320)
- Final Four: 160 pts/correct pick (2 games, max 320)
- Championship: 320 pts/correct pick (1 game, max 320)

**Note:** Later rounds are worth MORE per game. Getting the Final Four and Championship right is extremely valuable. Optimize accordingly.

## Rules

### What You CAN Do
- Modify ANY code in `predict.py` — variables, weights, logic, functions, structure
- Add new variables, parameters, helper functions
- Remove existing code that isn't helping
- Change the algorithm entirely (from seed-based to stat-based, hybrid, ML-inspired, etc.)
- Use any team stats available in the `team_stats` dict passed to `predict_bracket()`
- Add new heuristics, rules, or decision logic
- Use online resources for research if available

### What You CANNOT Do
- Modify any file other than `predict.py`
- Access actual tournament results (`game["winner"]`) in your prediction logic
- Use information from future years to predict past years (no data leakage)
- Make the exact same change that a previous agent already tried (check old_tests.md)
- Break the `predict_bracket(bracket, team_stats) -> list[dict]` interface
- Import external packages not in requirements.txt

### What You MUST Do
1. Read `docs/problem.md` for current knowledge about the algorithm
2. Read `docs/old_tests.md` for what's been tried before
3. Make exactly ONE conceptual change per attempt (can touch multiple lines)
4. The change must be different from any previous attempt logged in old_tests.md

## The Loop (handled by orchestrator — for your reference)

```
1. Read problem.md (accumulated knowledge)
2. Read old_tests.md (previous experiments)
3. Read current predict.py (current best algorithm)
4. Decide on ONE change to make
5. Apply the change to predict.py
6. Test: python scripts/run_test.py --json
7. If score improved → commit, update old_tests.md + problem.md
8. If score same/worse → git reset, log failure in old_tests.md
```

## How to Think About Changes

### High-Value Strategies
- **DRAMATIC changes**: Small parameter tweaks (e.g., 0.65->0.72) score +0.0 because they don't cross the 0.5 decision boundary. You MUST make BOLD changes. For example: changing SEED_WEIGHT from 0.7 to 0.0 (pure stats) improved the score by +27.5 points. Think in terms of 2x-10x changes, not 10% tweaks.
- **Pure stats model**: Setting SEED_WEIGHT=0.0 and STATS_WEIGHT=1.0 scores 997.5 (+27.5 over baseline 970.0). SRS is the strongest predictor. Consider building around SRS rather than seeds.
- **Later-round accuracy**: Championship game alone is worth 320 points. Small improvements in predicting Final Four / Elite 8 teams have outsized impact.
- **Restructure the algorithm**: Don't just tweak parameters. Consider entirely new approaches: pure SRS ranking, win_loss_pct-based, multi-stat composite scores, or custom formulas.
- **Stat integration**: SRS (Simple Rating System) is the single best predictor of tournament success. Use it heavily. Also consider: efg_pct, trb_pct, tov_pct, off_rtg.
- **Target specific flippable games**: 8v9 and 7v10 matchups are closest to the 0.5 boundary. Focus stat-based logic on these toss-up games where stats can be the tiebreaker.

### Common Pitfalls
- **Overfitting to one year**: A change that massively helps 2023 but hurts 2022/2024/2025 won't improve the average.
- **Ignoring later rounds**: Optimizing only for Round 1 accuracy leaves ~75% of points on the table.
- **Too many changes at once**: Hard to attribute improvements. Make one focused change.
- **Changing the interface**: predict_bracket() must keep its signature and return format.
- **CRITICAL: Small parameter tweaks that score +0.0**: The algorithm is deterministic. Small changes to weights/probabilities often don't cross the 0.5 decision threshold for any game. You MUST make changes large enough to actually flip specific game outcomes. Consider: changing the SEED_WIN_PROBABILITIES for specific matchups by 10-20%, adding entirely new stat factors with high weights, or restructuring the probability calculation entirely.
- **Not examining wrong predictions**: Before making a change, think about which games the baseline gets wrong and why. Target those specific failure modes.

## Data Available

### Bracket Structure (bracket dict)
Each game has: `game_id`, `round_num` (0-5), `team1` (name, seed), `team2` (name, seed), `winner` (DO NOT USE).

### Team Stats (team_stats dict)
Keys are team names, values are stat dicts. Available stats vary by year but may include:
- `wins`, `losses` — Win/loss record
- `srs` — Simple Rating System (points above average)
- `sos_all` — Strength of Schedule  
- `off_rtg` — Offensive efficiency (points per 100 possessions)
- `def_rtg` — Defensive efficiency (lower is better)
- `pace` — Possessions per game
- `fg_pct`, `fg3_pct`, `ft_pct` — Shooting percentages
- `trb`, `ast`, `stl`, `blk`, `tov` — Box score stats
- Various advanced metrics from Sports Reference

## Output Format

When you propose a change, describe:
1. **What** you're changing (specific variable, function, or logic)
2. **Why** you expect it to improve the score
3. **Risk** what could go wrong
4. **The actual code change** (full replacement of modified sections)

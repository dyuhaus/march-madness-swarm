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
- **Later-round accuracy**: Championship game alone is worth 320 points. Small improvements in predicting Final Four / Elite 8 teams have outsized impact.
- **Upset calibration**: The 5-12 and 6-11 matchups have the highest upset rates (~35%). If the current algorithm is too conservative or too aggressive on these, fixing it helps.
- **Stat integration**: If stats are available but underweighted, increasing their influence could help. Key stats: SRS, SOS, offensive/defensive efficiency.
- **Conference strength**: Teams from power conferences may have different upset profiles.
- **Seed matchup patterns**: 1-seeds almost never lose in Round 1, but 2-seeds occasionally do. Calibrate probabilities to historical reality.

### Common Pitfalls
- **Overfitting to one year**: A change that massively helps 2023 but hurts 2022/2024/2025 won't improve the average.
- **Ignoring later rounds**: Optimizing only for Round 1 accuracy leaves ~75% of points on the table.
- **Too many changes at once**: Hard to attribute improvements. Make one focused change.
- **Changing the interface**: predict_bracket() must keep its signature and return format.

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

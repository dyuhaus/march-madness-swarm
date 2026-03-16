# CLAUDE.md — March Madness Bracket Optimizer

## Project Identity

This is an evolutionary bracket optimization system. An agent swarm iteratively improves a March Madness prediction algorithm by testing changes against 4 years of historical data and keeping only improvements.

## Architecture

- **predict.py** — The algorithm. The ONLY file agents modify. Must maintain the `predict_bracket(bracket, team_stats) -> list[dict]` interface.
- **scripts/run_test.py** — Evaluation harness. Runs predict.py against all 4 years, returns averaged ESPN score. Use `--json` for machine-readable output.
- **scripts/scorer.py** — Scoring logic. ESPN standard: 10/20/40/80/160/320 per round.
- **scripts/scrape_data.py** — One-time data scraper. Populates `data/` from Sports Reference.
- **agents/orchestrator.py** — Swarm controller. Calls Claude API for agent "thinking", manages git.
- **docs/program.md** — Agent instructions (READ ONLY). Describes rules and strategy.
- **docs/old_tests.md** — Experiment log. All attempts recorded. Agents review before proposing.
- **docs/problem.md** — Knowledge base. Accumulated insights about what works/doesn't.

## Development Commands

```bash
# Run tests (human-readable)
python scripts/run_test.py --verbose

# Run tests (JSON for orchestrator)
python scripts/run_test.py --json

# Start the swarm
python agents/orchestrator.py --rounds 5

# Scrape data (first time only)
python scripts/scrape_data.py
```

## Critical Rules

1. **No data leakage**: predict.py must NEVER use `game["winner"]` or any actual tournament results
2. **Interface stability**: `predict_bracket(bracket, team_stats)` signature cannot change
3. **Test all 4 years**: Every change must be evaluated against 2022, 2023, 2024, 2025
4. **Git discipline**: Improvements are committed, failures are reverted, everything is logged

## Data Format

### Bracket JSON (`data/brackets/bracket_YYYY.json`)
```json
{
  "year": 2023,
  "games": [
    {
      "game_id": 0,
      "round_num": 0,
      "round": "Round of 64",
      "team1": {"name": "Alabama", "seed": 1},
      "team2": {"name": "Texas A&M-CC", "seed": 16},
      "winner": "Alabama"
    }
  ]
}
```

### Team Stats JSON (`data/team_stats/stats_YYYY.json`)
```json
{
  "Alabama": {
    "name": "Alabama",
    "wins": 29,
    "losses": 5,
    "srs": 19.5,
    "sos_all": 8.2,
    "off_rtg": 115.3,
    "def_rtg": 98.1
  }
}
```

## Setup Sequence (for first-time deployment)

1. Copy project to target directory
2. Run `python setup.py` (creates venv, GitHub repo, scrapes data, runs baseline)
3. Set `ANTHROPIC_API_KEY` environment variable
4. Run `python agents/orchestrator.py`

## Important Notes

- The scraper may hit rate limits on Sports Reference. If data is incomplete, you can manually populate the JSON files or use Claude Code with web access to look up bracket results.
- The orchestrator uses claude-sonnet-4-20250514 by default to minimize API costs.
- Each agent attempt costs ~1 API call. A full round (5 agents) = 5 calls.
- The actual test execution (running predictions, scoring) is pure local Python with zero API cost.

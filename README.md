# March Madness Bracket Optimizer — Agent Swarm

An autonomous agent swarm that iteratively optimizes a March Madness bracket prediction algorithm using an evolutionary improvement loop inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch).

## How It Works

1. **Baseline**: A seed algorithm predicts all 63 tournament games for 4 historical years (2022–2025)
2. **Scoring**: Predictions are scored using ESPN standard scoring (10/20/40/80/160/320 per round), averaged across all 4 years
3. **Swarm Loop**: 5 sequential agents each attempt one modification to the algorithm per round
4. **Keep or Revert**: If the modification improves the average score, it's committed as the new baseline. Otherwise, git resets.
5. **Learning**: All attempts (pass/fail) are logged. Agents review past experiments and accumulated knowledge before each attempt.

## Scoring (ESPN Standard)

| Round | Points per correct pick | Games | Max points |
|-------|------------------------|-------|------------|
| Round of 64 | 10 | 32 | 320 |
| Round of 32 | 20 | 16 | 320 |
| Sweet 16 | 40 | 8 | 320 |
| Elite 8 | 80 | 4 | 320 |
| Final Four | 160 | 2 | 320 |
| Championship | 320 | 1 | 320 |
| **Total** | | **63** | **1,920** |

## Project Structure

```
march-madness-swarm/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── setup.py                   # One-time setup: creates repo, installs deps, scrapes data
│
├── data/                      # Historical data (populated by setup.py)
│   ├── brackets/              # Tournament brackets + results (2022-2025)
│   │   ├── bracket_2022.json
│   │   ├── bracket_2023.json
│   │   ├── bracket_2024.json
│   │   └── bracket_2025.json
│   └── team_stats/            # Pre-tournament team statistics
│       ├── stats_2022.json
│       ├── stats_2023.json
│       ├── stats_2024.json
│       └── stats_2025.json
│
├── scripts/
│   ├── scrape_data.py         # Scrapes bracket results + team stats → data/
│   ├── scorer.py              # Scores predictions against actual results
│   └── run_test.py            # Runs predictor on all 4 years, returns avg score
│
├── predict.py                 # THE ALGORITHM — the only file agents modify
│
├── docs/
│   ├── program.md             # Agent instructions (READ ONLY for agents)
│   ├── old_tests.md           # Log of all attempted changes and results
│   └── problem.md             # Accumulated knowledge about the algorithm
│
├── agents/
│   └── orchestrator.py        # The swarm loop controller
│
└── .gitignore
```

## Key Files

### `predict.py` — The Algorithm (AGENTS MODIFY THIS)
The prediction algorithm. Takes a bracket (list of matchups with seeds + team stats) and returns predicted winners for all 63 games. Agents can change anything: variables, weights, logic, add new features, remove features, restructure entirely.

### `docs/program.md` — Agent Instructions (READ ONLY)
The rulebook for swarm agents. Describes what they can/cannot do, the testing loop, and how to log results. Agents read this but never modify it.

### `docs/old_tests.md` — Experiment Log (AGENTS APPEND TO THIS)
Every attempted change is logged here with: what was changed, the resulting score, whether it passed/failed, and notes on what improved/declined. Agents review this before proposing changes.

### `docs/problem.md` — Knowledge Base (AGENTS UPDATE THIS)
Fundamental understandings about the algorithm. "Increasing X causes Y to decrease." "Seed differential matters most in rounds 1-2." Agents update this with learnings from each experiment.

## Setup

### Prerequisites
- Python 3.10+
- Git with GitHub CLI (`gh`) configured
- Internet connection (for initial data scrape only)

### Quick Start

```bash
# 1. Clone this starter project to your working directory
#    (Copy to F:\_ClaudeAgents\march-madness-swarm\ or wherever you prefer)

# 2. Run setup — creates GitHub repo, installs deps, scrapes data
python setup.py

# 3. Run the baseline test to verify everything works
python scripts/run_test.py

# 4. Start the swarm (runs agents sequentially)
python agents/orchestrator.py
```

## Data Sources

- **Bracket data**: Scraped from ESPN bracket pages + Sports Reference
- **Team statistics**: Scraped from Sports Reference (sports-reference.com/cbb/)
  - Includes: Win/Loss, SOS, SRS, pace, offensive/defensive ratings, shooting splits, turnover rates, rebound rates, and more
- **All data is pre-tournament only** — no future leakage

## Design Decisions

- **Sequential agents**: Agents run one at a time to avoid merge conflicts. Each agent always works from the latest best version.
- **Offline testing**: All bracket scoring runs locally against pre-scraped data. Zero API cost for test execution.
- **Git as memory**: Every improvement is a commit. The git log IS the optimization history.
- **ESPN scoring incentivizes later rounds**: Getting the championship right (320 pts) is worth as much as getting 32 first-round games right. The algorithm should weight later-round accuracy.

## For Claude Code

When implementing this project, work in this order:

1. **Phase 1**: Run `setup.py` to create the GitHub repo and install dependencies
2. **Phase 2**: Run `scripts/scrape_data.py` to populate the `data/` folder
3. **Phase 3**: Run `python scripts/run_test.py` to establish baseline score
4. **Phase 4**: Run `python agents/orchestrator.py` to start the swarm

The orchestrator handles everything: reading program.md, calling the API for agent "thinking", applying changes, testing, scoring, committing/reverting, and logging.

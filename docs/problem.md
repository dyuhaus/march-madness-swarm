# Problem Knowledge Base

Accumulated understanding of how the bracket prediction algorithm works, what affects scoring, and fundamental relationships between variables and outcomes.

Agents MUST read this before making changes. Agents SHOULD update this with new learnings after each experiment.

---

## Algorithm Overview

The current algorithm (`predict.py`) predicts tournament game winners using:
1. **Seed-based probability**: Historical upset rates for each seed matchup (1v16, 2v15, etc.)
2. **Round decay**: Seed advantage is reduced in later rounds
3. **Stats adjustment**: Team statistics (when available) slightly shift the prediction

The seed probability and stats adjustment are combined as a weighted average (70% seed, 30% stats by default).

## Known Facts

### About March Madness Scoring (ESPN)
- 1,920 maximum points per bracket
- Later rounds are dramatically more valuable per game
- Getting the champion right (320 pts) = getting 32 first-round games right (320 pts)
- The Final Four + Championship = 960 pts (50% of total possible)
- Implication: accuracy on 1-3 seeds in later rounds is extremely high-leverage

### About March Madness Historically
- 1-seeds have won the championship ~50% of the time
- A 1-seed has NEVER lost to a 16-seed in the men's tournament (until 2018: UMBC over Virginia)
- 12-over-5 upsets happen roughly 35% of the time
- 11-over-6 upsets happen roughly 37% of the time
- Since 2000, at least one double-digit seed has reached the Elite 8 almost every year
- The Final Four typically includes 2-3 teams seeded 1-3

### About the Data
- Team stats come from Sports Reference and may have varying field names across years
- Not all teams in the bracket may have stats available (name matching issues)
- Stats represent regular season performance — tournament performance can differ
- Stats available may include: wins, losses, SRS, SOS, offensive/defensive ratings, shooting splits

## Discovered Relationships

*This section will be updated as experiments reveal how changes affect the score.*

### Variables and Their Effects
*(Format: Variable → Effect on score)*

- *(No experiments run yet)*

### Successful Strategies
*(Changes that improved the score)*

- *(No experiments run yet)*

### Failed Strategies  
*(Changes that hurt or had no effect)*

- *(No experiments run yet)*

## Open Questions

- What is the optimal balance between seed weight and stats weight?
- Does adding more stats improve prediction, or does it add noise?
- Are there round-specific strategies that help (e.g., always pick 1-seeds through Sweet 16)?
- How much does the round decay factor affect later-round accuracy?
- Would a completely different model architecture (e.g., Elo-based, regression-based) outperform the current weighted approach?

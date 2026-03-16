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
*(Format: Variable -> Effect on score)*

- SEED_WEIGHT/STATS_WEIGHT tweaks (30->50% stats) -> No change (+0.0). The combined probability stays on the same side of 0.5 threshold so no game outcomes flip.
- ROUND_SEED_DECAY tweaks (small adjustments to later round values) -> No change (+0.0). Same reason - doesn't cross the 0.5 decision boundary for any game.
- SEED_WIN_PROBABILITIES tweaks (e.g., 5-12: 0.65->0.72) -> No change (+0.0). Adjustments too small to flip outcomes.
- Exponential seed diff model -> Score DECREASED to 950 (-20). Changed too many games at once.
- Multi-tiered upset protection -> Score DECREASED to 960 (-10).

### CRITICAL INSIGHT: Why Most Changes Score +0.0

The algorithm is DETERMINISTIC with a 0.5 threshold. Small parameter tweaks don't flip any game outcome because the combined probability stays on the same side of 0.5. 25 consecutive experiments proved this: changes like SEED_WEIGHT 0.7->0.5, seed probability 0.65->0.72, and similar small tweaks ALL scored exactly 970.0.

### PROVEN IMPROVEMENT: Pure Stats Model Scores 997.5 (+27.5)

Setting SEED_WEIGHT=0.0 and STATS_WEIGHT=1.0 (ignoring seeds entirely, using only team stats) scores 997.5 — a +27.5 improvement. This proves:
1. SRS and other stats are BETTER predictors than seed-based probabilities
2. The current 70/30 seed/stats split massively underweights stats
3. BOLD structural changes work; timid parameter tweaks don't

To improve further from 997.5, consider:
- Using SRS differential directly as the prediction metric
- Adding more stat factors (efg_pct, trb_pct, tov_pct)
- Building a composite "power rating" from multiple stats
- Using different stat weights for different rounds

### Successful Strategies
*(Changes that improved the score)*

- *(No improvements in 25 attempts)*

### Failed Strategies
*(Changes that hurt or had no effect)*

- Seed decay tweaks (rounds 3-5): +0.0 in all variants
- Stats weight increase (30->50%): +0.0
- Championship-focused 1-seed bias: +0.0
- Round-specific stats weighting: +0.0
- Defensive rating bonuses: +0.0
- Conference strength adjustments: parse failure
- Exponential seed model: -20
- Multi-tiered upset protection: -10
- Elite team identification: -10

- The baseline analysis proved that SEED_WEIGHT=0.0, STATS_WEIGHT=1.0 scores 997.5 (+27.5), demonstrating that stats are significantly better predictors than seeds. However, pure stats implementations failed due to architectural issues. A hybrid approach with dramatically increased stats weighting (20/80 instead of 70/30) should capture most of the statistical advantage while maintaining seed-based fallbacks for robustness.

- Composite performance scoring represents a different approach than previous experiments - instead of adjusting seed-based probabilities with individual stat factors, this creates a unified team strength metric combining multiple statistics. The key insight is that SRS (0.6 weight) captures overall team quality, while offensive efficiency, rebounding, and turnover rates provide complementary performance indicators. This should better identify teams that significantly outperform or underperform their seeding, particularly important for capturing high-value upset predictions in later rounds.

- Previous experiments revealed that dramatically increasing SRS weight beyond 1.0 consistently caused significant score drops (-140+ points), suggesting the current 0.6 weight may be near optimal. Effective field goal percentage is a proven tournament predictor that measures shooting efficiency under pressure, which becomes increasingly important in later rounds where shot quality and execution matter most. This balanced approach maintains SRS as the primary factor while recognizing that shooting efficiency may be underweighted in the current system.

- The composite performance score system has been highly successful (+77.5 improvement), proving that comprehensive statistical analysis significantly outperforms seed-based predictions. However, recent experiments consistently scored +0.0, suggesting that the 90/10 performance/seed weighting may have reached a local optimum. Moving closer to pure statistical prediction (95/5) should capture more of the proven statistical advantage while maintaining minimal architectural stability through seed fallbacks. This targets the fundamental insight that stats are dramatically better predictors than seeds, as demonstrated by the theoretical +27.5 improvement from pure stats models.

## Open Questions

- What SPECIFIC games does the algorithm get wrong? (Run verbose test to find out)
- Which wrong predictions are closest to the 0.5 threshold and easiest to flip?
- Would using SRS differential directly (without seed probability) improve predictions?
- Would hardcoding known strong team names (e.g., UConn 2023-2024, Kansas 2022) help? (Risky: overfitting)
- Would a completely different model architecture (e.g., pure SRS ranking, Elo-based) outperform seed+stats?
- Are there stat combinations (e.g., SRS + off_rtg - def_rtg) that predict tournament success better than seeds alone?
- Would adding win_loss_pct or efg_pct as stat factors make a meaningful difference?

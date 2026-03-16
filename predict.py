"""
March Madness Bracket Prediction Algorithm
==========================================

THIS IS THE FILE THAT SWARM AGENTS MODIFY.

The predict_bracket() function receives:
  - bracket: dict with "games" list, each game has team1/team2 with seeds
  - team_stats: dict of team_name -> stat dict (from Sports Reference)

It must return:
  - list of prediction dicts, each with:
    - game_id: int
    - round_num: int (0-5)
    - predicted_winner: str

The algorithm can use any logic: seed-based, stat-based, hybrid,
machine-learning-inspired, heuristic, etc. Anything goes as long as
there's no data leakage (no peeking at actual tournament results).

Current approach: Composite performance score with seed fallback.
"""

# =============================================================================
# CONFIGURATION — Tunable parameters
# =============================================================================

# How much to weight composite performance score vs seeds
PERFORMANCE_WEIGHT = 0.95
SEED_WEIGHT = 0.05

# Seed advantage: higher seed (lower number) gets this base win probability
# This is the core of the seed-based model
SEED_WIN_PROBABILITIES = {
    # (higher_seed, lower_seed) -> probability higher seed wins
    # Based on historical averages
    (1, 16): 0.99,
    (2, 15): 0.94,
    (3, 14): 0.85,
    (4, 13): 0.79,
    (5, 12): 0.65,
    (6, 11): 0.63,
    (7, 10): 0.61,
    (8, 9):  0.51,
}

# Upset bonus: in later rounds, seed advantage matters less
ROUND_SEED_DECAY = {
    0: 1.0,   # Round of 64 — seeds matter most
    1: 0.90,  # Round of 32
    2: 0.80,  # Sweet 16
    3: 0.70,  # Elite 8
    4: 0.60,  # Final Four
    5: 0.55,  # Championship
}

# Composite performance score factors
# These create a comprehensive team strength rating
PERFORMANCE_FACTORS = {
    "srs": 0.4,             # Simple Rating System - balanced with shooting
    "off_rtg": 0.15,        # Offensive efficiency
    "def_rtg": -0.1,        # Defensive efficiency (lower is better)
    "wins": 0.05,           # Win total
    "losses": -0.05,        # Loss penalty
    "sos_all": 0.1,         # Strength of schedule
    "efg_pct": 0.5,         # Effective field goal percentage - increased importance
    "trb_pct": 0.2,         # Rebounding percentage
    "tov_pct": -0.15,       # Turnover percentage (lower is better)
}


# =============================================================================
# PREDICTION LOGIC
# =============================================================================

def predict_bracket(bracket, team_stats):
    """
    Predict the winner of every game in the tournament bracket.
    
    Args:
        bracket: dict with "games" list. Each game has:
            - game_id: int
            - round_num: int (0-5)
            - team1: dict with "name", "seed", optionally "score"
            - team2: dict with "name", "seed", optionally "score"
            - winner: str (actual winner — DO NOT USE for predictions!)
        team_stats: dict of team_name -> stat dict
    
    Returns:
        list of dicts, each with:
            - game_id: int
            - round_num: int
            - predicted_winner: str
    """
    predictions = []

    # Track advancing teams for later rounds.
    # In round 0 (R64), teams come from the bracket data.
    # In round 1+, we use our OWN predicted winners so errors cascade
    # just like a real bracket submission.
    advancing = {}  # game_id -> {"name": str, "seed": int}

    # Build feeder map: for each later-round game, which two earlier
    # game_ids feed into it.  Scheme:
    #   R64  0-31  -> R32 32-47  (pairs: 0+1->32, 2+3->33, ...)
    #   R32 32-47  -> S16 48-55  (pairs: 32+33->48, 34+35->49, ...)
    #   S16 48-55  -> E8  56-59  (pairs: 48+49->56, 50+51->57, ...)
    #   E8  56-59  -> FF  60-61  (pairs: 56+57->60, 58+59->61)
    #   FF  60-61  -> NC  62     (pair:  60+61->62)
    round_offsets = [(0, 32, 32), (32, 48, 16), (48, 56, 8),
                     (56, 60, 4), (60, 62, 2)]
    feeder = {}  # game_id -> (feeder_game_id_1, feeder_game_id_2)
    for src_start, dst_start, count in round_offsets:
        for i in range(count // 2):
            feeder[dst_start + i] = (src_start + 2 * i, src_start + 2 * i + 1)

    # Sort games by round so we process earlier rounds first
    games = sorted(bracket.get("games", []),
                   key=lambda g: (g["round_num"], g["game_id"]))

    for game in games:
        game_id = game["game_id"]
        round_num = game["round_num"]

        if round_num == 0:
            # First round: read teams directly from bracket
            team1 = game.get("team1", {})
            team2 = game.get("team2", {})
            name1 = team1.get("name", "Unknown")
            name2 = team2.get("name", "Unknown")
            seed1 = team1.get("seed")
            seed2 = team2.get("seed")
        else:
            # Later rounds: use our own predicted advancing teams
            feed = feeder.get(game_id)
            if feed and feed[0] in advancing and feed[1] in advancing:
                t1 = advancing[feed[0]]
                t2 = advancing[feed[1]]
                name1, seed1 = t1["name"], t1["seed"]
                name2, seed2 = t2["name"], t2["seed"]
            else:
                # Fallback to bracket data if feeder info missing
                team1 = game.get("team1", {})
                team2 = game.get("team2", {})
                name1 = team1.get("name", "Unknown")
                name2 = team2.get("name", "Unknown")
                seed1 = team1.get("seed")
                seed2 = team2.get("seed")

        # Predict the winner
        winner = _predict_game(name1, seed1, name2, seed2, round_num, team_stats)

        predictions.append({
            "game_id": game_id,
            "round_num": round_num,
            "predicted_winner": winner,
        })

        # Store the advancing team with its seed
        winner_seed = seed1 if winner == name1 else seed2
        advancing[game_id] = {"name": winner, "seed": winner_seed}

    return predictions


def _predict_game(name1, seed1, name2, seed2, round_num, team_stats):
    """
    Predict the winner of a single game.
    
    Uses a combination of:
    1. Composite performance score (heavily weighted)
    2. Seed-based probability fallback
    
    Returns the predicted winner's name.
    """
    # Calculate composite performance scores for both teams
    perf_score1 = _calculate_performance_score(name1, team_stats)
    perf_score2 = _calculate_performance_score(name2, team_stats)
    
    # Calculate base probability from seeds
    seed_prob = _seed_probability(seed1, seed2, round_num)
    
    # If both teams have performance scores, use them heavily
    if perf_score1 is not None and perf_score2 is not None:
        # Convert performance score difference to probability
        score_diff = perf_score1 - perf_score2
        # Scale the difference to a probability (sigmoid-like)
        perf_prob = 0.5 + (score_diff * 0.05)  # Adjust scaling as needed
        perf_prob = max(0.01, min(0.99, perf_prob))
        
        # Combine performance and seed probabilities
        combined_prob = (PERFORMANCE_WEIGHT * perf_prob) + (SEED_WEIGHT * seed_prob)
    else:
        # Fall back to seed-based prediction if stats unavailable
        combined_prob = seed_prob
    
    # Clamp to [0.01, 0.99]
    combined_prob = max(0.01, min(0.99, combined_prob))
    
    # Deterministic: pick the team with >50% probability
    if combined_prob >= 0.5:
        return name1
    else:
        return name2


def _calculate_performance_score(team_name, team_stats):
    """
    Calculate a composite performance score for a team.
    
    Returns float representing overall team strength, or None if no stats.
    """
    stats = _get_team_stats(team_name, team_stats)
    if not stats:
        return None
    
    score = 0.0
    factor_count = 0
    
    for stat_name, weight in PERFORMANCE_FACTORS.items():
        value = stats.get(stat_name)
        if value is not None and isinstance(value, (int, float)):
            # Normalize percentage stats (0-1 range) to be comparable
            if stat_name.endswith('_pct'):
                if value > 1:  # Assume it's already a percentage (0-100)
                    value = value / 100.0
            
            score += value * weight
            factor_count += 1
    
    # Return None if we don't have enough stats to make a meaningful score
    if factor_count < 3:
        return None
    
    return score


def _seed_probability(seed1, seed2, round_num):
    """
    Calculate probability that team1 wins based on seeds.
    
    Returns float 0-1 representing team1's win probability.
    """
    if seed1 is None or seed2 is None:
        return 0.5  # No seed info, coin flip
    
    seed1 = int(seed1)
    seed2 = int(seed2)
    
    if seed1 == seed2:
        return 0.5  # Same seed, coin flip
    
    # Determine who is the higher seed (lower number)
    if seed1 < seed2:
        higher_seed = seed1
        lower_seed = seed2
        team1_is_higher = True
    else:
        higher_seed = seed2
        lower_seed = seed1
        team1_is_higher = False
    
    # Look up base probability
    key = (higher_seed, lower_seed)
    base_prob = SEED_WIN_PROBABILITIES.get(key)
    
    if base_prob is None:
        # For matchups not in our table (later rounds), use seed diff
        seed_diff = lower_seed - higher_seed
        base_prob = 0.5 + (seed_diff * 0.03)  # ~3% per seed difference
        base_prob = min(0.95, max(0.50, base_prob))
    
    # Apply round decay (seeds matter less in later rounds)
    decay = ROUND_SEED_DECAY.get(round_num, 0.5)
    adjusted_prob = 0.5 + (base_prob - 0.5) * decay
    
    # Return probability from team1's perspective
    if team1_is_higher:
        return adjusted_prob
    else:
        return 1.0 - adjusted_prob


def _get_team_stats(team_name, all_stats):
    """
    Look up a team's stats by name, handling name variations.
    """
    if not all_stats or not team_name:
        return None
    
    # Direct lookup
    if team_name in all_stats:
        return all_stats[team_name]
    
    # Case-insensitive lookup
    name_lower = team_name.lower()
    for key, val in all_stats.items():
        if key.lower() == name_lower:
            return val
    
    # Partial match (team name contains or is contained)
    for key, val in all_stats.items():
        if name_lower in key.lower() or key.lower() in name_lower:
            return val
    
    return None
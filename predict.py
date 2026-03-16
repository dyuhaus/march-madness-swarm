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

Current approach: Seed-based baseline with stat adjustments.
"""

# =============================================================================
# CONFIGURATION — Tunable parameters
# =============================================================================

# How much to weight seed differential vs stats
SEED_WEIGHT = 0.7
STATS_WEIGHT = 0.3

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

# Stats that improve a team's win probability (if available)
# Each stat has a weight indicating how much it contributes
STAT_FACTORS = {
    "wins": 0.02,           # More wins = slight boost
    "losses": -0.03,        # More losses = slight penalty
    "srs": 0.03,            # Simple Rating System (Sports Ref)
    "sos_all": 0.02,        # Strength of Schedule
    "off_rtg": 0.01,        # Offensive rating
    "def_rtg": -0.01,       # Defensive rating (lower is better)
    "pace": 0.0,            # Pace (neutral by default)
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
    
    # Track advancing teams for later rounds
    # In round 0 (R64), all teams are from the bracket
    # In round 1+, we need to use our own predictions
    advancing = {}  # game_id -> predicted winner
    
    # Sort games by round so we process earlier rounds first
    games = sorted(bracket.get("games", []), key=lambda g: (g["round_num"], g["game_id"]))
    
    for game in games:
        game_id = game["game_id"]
        round_num = game["round_num"]
        
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
        
        advancing[game_id] = winner
    
    return predictions


def _predict_game(name1, seed1, name2, seed2, round_num, team_stats):
    """
    Predict the winner of a single game.
    
    Uses a combination of:
    1. Seed-based probability (historical upset rates)
    2. Team stats adjustment (when available)
    
    Returns the predicted winner's name.
    """
    # Calculate base probability from seeds
    seed_prob = _seed_probability(seed1, seed2, round_num)
    
    # Calculate stats adjustment
    stats_adj = _stats_adjustment(name1, name2, team_stats)
    
    # Combine: weighted average
    # seed_prob is probability that team1 wins (0 to 1)
    # stats_adj is adjustment favoring team1 (negative = favors team2)
    combined_prob = (SEED_WEIGHT * seed_prob) + (STATS_WEIGHT * (0.5 + stats_adj))
    
    # Clamp to [0.01, 0.99]
    combined_prob = max(0.01, min(0.99, combined_prob))
    
    # Deterministic: pick the team with >50% probability
    if combined_prob >= 0.5:
        return name1
    else:
        return name2


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


def _stats_adjustment(name1, name2, team_stats):
    """
    Calculate a stats-based adjustment favoring team1 or team2.
    
    Returns float: positive favors team1, negative favors team2.
    Range roughly [-0.5, 0.5].
    """
    stats1 = _get_team_stats(name1, team_stats)
    stats2 = _get_team_stats(name2, team_stats)
    
    if not stats1 and not stats2:
        return 0.0  # No stats available
    
    adjustment = 0.0
    
    for stat_name, weight in STAT_FACTORS.items():
        val1 = stats1.get(stat_name, 0) if stats1 else 0
        val2 = stats2.get(stat_name, 0) if stats2 else 0
        
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            diff = val1 - val2
            adjustment += diff * weight
    
    # Normalize to roughly [-0.5, 0.5]
    adjustment = max(-0.5, min(0.5, adjustment))
    
    return adjustment


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

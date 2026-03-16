"""
Bracket scorer using ESPN standard scoring.

Compares predicted bracket against actual results and returns
a score breakdown by round.

ESPN Standard Scoring:
  Round of 64:    10 pts per correct pick
  Round of 32:    20 pts per correct pick
  Sweet 16:       40 pts per correct pick
  Elite 8:        80 pts per correct pick
  Final Four:    160 pts per correct pick
  Championship:  320 pts per correct pick
  
  Maximum possible: 1,920 points
"""

import json

# ESPN Standard Scoring
POINTS_PER_ROUND = {
    0: 10,   # Round of 64
    1: 20,   # Round of 32
    2: 40,   # Sweet 16
    3: 80,   # Elite 8
    4: 160,  # Final Four
    5: 320,  # Championship
}

ROUND_NAMES = {
    0: "Round of 64",
    1: "Round of 32",
    2: "Sweet 16",
    3: "Elite 8",
    4: "Final Four",
    5: "Championship",
}

MAX_GAMES_PER_ROUND = {
    0: 32,
    1: 16,
    2: 8,
    3: 4,
    4: 2,
    5: 1,
}

MAX_TOTAL = 1920


def score_bracket(predictions, actual_results):
    """
    Score a predicted bracket against actual results.
    
    Args:
        predictions: list of dicts, each with:
            - game_id: int
            - round_num: int (0-5)
            - predicted_winner: str (team name)
        actual_results: list of dicts (from bracket JSON), each with:
            - game_id: int
            - round_num: int (0-5)
            - winner: str (team name)
    
    Returns:
        dict with:
            - total_score: int
            - max_possible: int (1920)
            - percentage: float
            - by_round: dict of round_num -> {correct, total, points, max_points}
            - correct_picks: int
            - total_picks: int
            - details: list of per-game results
    """
    # Index actual results by game_id
    actual_by_id = {}
    for game in actual_results:
        actual_by_id[game["game_id"]] = game
    
    total_score = 0
    correct_picks = 0
    total_picks = 0
    
    by_round = {}
    for r in range(6):
        by_round[r] = {
            "name": ROUND_NAMES[r],
            "correct": 0,
            "total": 0,
            "points": 0,
            "max_points": MAX_GAMES_PER_ROUND[r] * POINTS_PER_ROUND[r],
        }
    
    details = []
    
    for pred in predictions:
        game_id = pred["game_id"]
        round_num = pred["round_num"]
        predicted = pred["predicted_winner"]
        
        actual_game = actual_by_id.get(game_id)
        if not actual_game:
            details.append({
                "game_id": game_id,
                "round": ROUND_NAMES.get(round_num, "Unknown"),
                "predicted": predicted,
                "actual": "N/A",
                "correct": False,
                "points": 0,
                "note": "No actual result found"
            })
            continue
        
        actual_winner = actual_game.get("winner", "")
        is_correct = _names_match(predicted, actual_winner)
        
        points = POINTS_PER_ROUND.get(round_num, 0) if is_correct else 0
        total_score += points
        total_picks += 1
        
        if is_correct:
            correct_picks += 1
        
        by_round[round_num]["total"] += 1
        if is_correct:
            by_round[round_num]["correct"] += 1
            by_round[round_num]["points"] += points
        
        details.append({
            "game_id": game_id,
            "round": ROUND_NAMES.get(round_num, "Unknown"),
            "predicted": predicted,
            "actual": actual_winner,
            "correct": is_correct,
            "points": points,
        })
    
    return {
        "total_score": total_score,
        "max_possible": MAX_TOTAL,
        "percentage": round(total_score / MAX_TOTAL * 100, 1) if MAX_TOTAL > 0 else 0,
        "correct_picks": correct_picks,
        "total_picks": total_picks,
        "pick_accuracy": round(correct_picks / total_picks * 100, 1) if total_picks > 0 else 0,
        "by_round": by_round,
        "details": details,
    }


def _names_match(name1, name2):
    """
    Fuzzy match team names to handle variations.
    e.g., "UConn" vs "Connecticut", "St. John's" vs "Saint John's"
    """
    if not name1 or not name2:
        return False
    
    # Exact match
    if name1.strip().lower() == name2.strip().lower():
        return True
    
    # Normalize common variations
    n1 = _normalize_name(name1)
    n2 = _normalize_name(name2)
    
    if n1 == n2:
        return True
    
    # Check if one is a substring of the other (for partial matches)
    if len(n1) > 4 and len(n2) > 4:
        if n1 in n2 or n2 in n1:
            return True
    
    return False


def _normalize_name(name):
    """Normalize a team name for comparison."""
    name = name.strip().lower()
    
    # Common replacements
    replacements = {
        "st.": "saint",
        "st ": "saint ",
        "uconn": "connecticut",
        "unc": "north carolina",
        "lsu": "louisiana state",
        "osu": "ohio state",
        "fau": "florida atlantic",
        "fdu": "fairleigh dickinson",
        "sdsu": "san diego state",
        "ucsd": "uc san diego",
        "vcu": "virginia commonwealth",
        "smu": "southern methodist",
        "tcu": "texas christian",
        "byu": "brigham young",
        "usc": "southern california",
        "ucf": "central florida",
        "utsa": "ut san antonio",
        "etsu": "east tennessee state",
        "mtsu": "middle tennessee",
        "utep": "texas el paso",
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove common suffixes/prefixes
    name = name.replace("university", "").replace("college", "")
    name = name.replace("state", "st").replace("(", "").replace(")", "")
    name = name.strip()
    
    return name


def format_scorecard(result):
    """Format a score result as a readable string."""
    lines = []
    lines.append(f"Total Score: {result['total_score']} / {result['max_possible']} ({result['percentage']}%)")
    lines.append(f"Correct Picks: {result['correct_picks']} / {result['total_picks']} ({result['pick_accuracy']}%)")
    lines.append("")
    lines.append("By Round:")
    
    for r in range(6):
        rd = result["by_round"][r]
        lines.append(
            f"  {rd['name']:20s}: {rd['correct']:2d}/{rd['total']:2d} correct, "
            f"{rd['points']:4d}/{rd['max_points']:4d} pts"
        )
    
    return "\n".join(lines)

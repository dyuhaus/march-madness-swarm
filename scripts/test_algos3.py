"""Test z-score normalized composite and other advanced approaches."""
import json, sys, subprocess, os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREDICT_PY = os.path.join(PROJECT_DIR, "predict.py")
original = open(PREDICT_PY, encoding='utf-8').read()

def test_algo(name, code):
    with open(PREDICT_PY, 'w', encoding='utf-8') as f:
        f.write(code)
    r = subprocess.run([sys.executable, '-B', os.path.join(PROJECT_DIR, 'scripts', 'run_test.py'), '--json'],
                       capture_output=True, text=True, cwd=PROJECT_DIR)
    with open(PREDICT_PY, 'w', encoding='utf-8') as f:
        f.write(original)
    if r.returncode == 0:
        s = json.loads(r.stdout.strip())
        yrs = {k: v['total_score'] for k, v in s['per_year'].items()}
        return s['average_score'], yrs
    return None, None

# Z-score normalized composite
algo_zscore = '''
import math

def predict_bracket(bracket, team_stats):
    # Pre-compute z-scores for all stats
    z_stats = _compute_z_scores(team_stats)

    predictions = []
    advancing = {}
    round_offsets = [(0, 32, 32), (32, 48, 16), (48, 56, 8), (56, 60, 4), (60, 62, 2)]
    feeder = {}
    for src_start, dst_start, count in round_offsets:
        for i in range(count // 2):
            feeder[dst_start + i] = (src_start + 2 * i, src_start + 2 * i + 1)
    games = sorted(bracket.get("games", []), key=lambda g: (g["round_num"], g["game_id"]))
    for game in games:
        game_id = game["game_id"]
        round_num = game["round_num"]
        if round_num == 0:
            name1, seed1 = game["team1"]["name"], game["team1"]["seed"]
            name2, seed2 = game["team2"]["name"], game["team2"]["seed"]
        else:
            feed = feeder.get(game_id)
            if feed and feed[0] in advancing and feed[1] in advancing:
                name1, seed1 = advancing[feed[0]]["name"], advancing[feed[0]]["seed"]
                name2, seed2 = advancing[feed[1]]["name"], advancing[feed[1]]["seed"]
            else:
                name1, seed1 = game["team1"]["name"], game["team1"]["seed"]
                name2, seed2 = game["team2"]["name"], game["team2"]["seed"]

        r1 = _power_rating(name1, z_stats)
        r2 = _power_rating(name2, z_stats)

        if r1 is not None and r2 is not None:
            winner = name1 if r1 >= r2 else name2
        else:
            winner = name1 if (seed1 or 16) <= (seed2 or 16) else name2

        predictions.append({"game_id": game_id, "round_num": round_num, "predicted_winner": winner})
        advancing[game_id] = {"name": winner, "seed": seed1 if winner == name1 else seed2}
    return predictions

STAT_WEIGHTS = {WEIGHTS}

def _compute_z_scores(team_stats):
    """Compute z-scores for all stats across all teams."""
    if not team_stats:
        return {}

    # Collect all values for each stat
    stat_values = {}
    for team, stats in team_stats.items():
        for stat_name in STAT_WEIGHTS:
            val = stats.get(stat_name)
            if val is not None and isinstance(val, (int, float)):
                stat_values.setdefault(stat_name, []).append((team, val))

    # Compute mean and std for each stat
    z_scores = {}  # team -> {stat: z_score}
    for stat_name, values in stat_values.items():
        vals = [v for _, v in values]
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / max(len(vals) - 1, 1)
        std = math.sqrt(variance) if variance > 0 else 1.0

        for team, val in values:
            if team not in z_scores:
                z_scores[team] = {}
            z_scores[team][stat_name] = (val - mean) / std

    return z_scores

def _power_rating(name, z_stats):
    """Calculate power rating using z-scored stats."""
    # Try exact match, then fuzzy
    zs = z_stats.get(name)
    if not zs:
        nl = name.lower()
        for k, v in z_stats.items():
            if k.lower() == nl:
                zs = v; break
        if not zs:
            for k, v in z_stats.items():
                if nl in k.lower() or k.lower() in nl:
                    zs = v; break
    if not zs:
        return None

    score = 0.0
    count = 0
    for stat_name, weight in STAT_WEIGHTS.items():
        z = zs.get(stat_name)
        if z is not None:
            score += z * weight
            count += 1

    return score if count >= 2 else None
'''

print(f"{'Algorithm':30s} {'Avg':>7s} {'2022':>6s} {'2023':>6s} {'2024':>6s} {'2025':>6s}")
print("-" * 75)

avg, yrs = test_algo("current", original)
if avg: print(f"{'current':30s} {avg:>7.1f} {yrs['2022']:>6} {yrs['2023']:>6} {yrs['2024']:>6} {yrs['2025']:>6}")

# Test various z-score weight combinations
weight_configs = {
    "zscore_srs_only": '{"srs": 1.0}',
    "zscore_srs+sos": '{"srs": 1.0, "sos": 0.5}',
    "zscore_srs+off": '{"srs": 1.0, "off_rtg": 0.5}',
    "zscore_srs+off+sos": '{"srs": 1.0, "off_rtg": 0.3, "sos": 0.3}',
    "zscore_balanced": '{"srs": 1.0, "off_rtg": 0.3, "sos": 0.3, "efg_pct": 0.2, "tov_pct": -0.2}',
    "zscore_defense": '{"srs": 1.0, "off_rtg": 0.2, "tov_pct": -0.3, "trb_pct": 0.2}',
    "zscore_tourney": '{"srs": 1.0, "sos": 0.5, "off_rtg": 0.2, "tov_pct": -0.2, "efg_pct": 0.2}',
    "zscore_heavy_sos": '{"srs": 0.8, "sos": 0.8, "off_rtg": 0.2}',
    "zscore_all": '{"srs": 0.8, "sos": 0.4, "off_rtg": 0.3, "efg_pct": 0.2, "tov_pct": -0.2, "trb_pct": 0.15, "stl_pct": 0.1, "win_loss_pct": 0.3}',
    "zscore_wl_focus": '{"srs": 0.6, "win_loss_pct": 0.8, "sos": 0.3}',
}

for name, weights_str in weight_configs.items():
    code = algo_zscore.replace("{WEIGHTS}", weights_str)
    avg, yrs = test_algo(name, code)
    if avg:
        print(f"{name:30s} {avg:>7.1f} {yrs['2022']:>6} {yrs['2023']:>6} {yrs['2024']:>6} {yrs['2025']:>6}")
    else:
        print(f"{name:30s} FAILED")

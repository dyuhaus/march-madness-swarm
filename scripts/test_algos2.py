"""Test fundamentally different algorithm structures."""
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

CORE = '''
def predict_bracket(bracket, team_stats):
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
        winner = _pick(name1, seed1, name2, seed2, round_num, team_stats)
        predictions.append({"game_id": game_id, "round_num": round_num, "predicted_winner": winner})
        advancing[game_id] = {"name": winner, "seed": seed1 if winner == name1 else seed2}
    return predictions

def _lookup(name, stats):
    if not stats or not name:
        return None
    s = stats.get(name)
    if not s:
        nl = name.lower()
        for k, v in stats.items():
            if k.lower() == nl:
                return v
        for k, v in stats.items():
            if nl in k.lower() or k.lower() in nl:
                return v
    return s
'''

# Algo A: Round-specific strategy (stats for early, seeds for late)
algo_round_specific = CORE + '''
def _pick(name1, seed1, name2, seed2, round_num, all_stats):
    s1 = _lookup(name1, all_stats)
    s2 = _lookup(name2, all_stats)
    srs1 = s1.get("srs", 0) if s1 else 0
    srs2 = s2.get("srs", 0) if s2 else 0
    sd1 = seed1 or 8
    sd2 = seed2 or 8

    if round_num <= 1:
        # Early rounds: pure stats
        if s1 and s2 and (srs1 != 0 or srs2 != 0):
            return name1 if srs1 >= srs2 else name2
        return name1 if sd1 <= sd2 else name2
    elif round_num <= 3:
        # Mid rounds: blend stats and seed
        srs_diff = srs1 - srs2
        seed_diff = sd2 - sd1
        score = srs_diff * 0.7 + seed_diff * 2.0
        return name1 if score >= 0 else name2
    else:
        # FF/Championship: favor seeds more (1-seeds often win)
        seed_diff = sd2 - sd1
        srs_diff = srs1 - srs2
        score = srs_diff * 0.3 + seed_diff * 3.0
        return name1 if score >= 0 else name2
'''

# Algo B: SRS-dominant with "road warrior" bonus (wins_visitor)
algo_road_warrior = CORE + '''
def _pick(name1, seed1, name2, seed2, round_num, all_stats):
    r1 = _power(name1, all_stats)
    r2 = _power(name2, all_stats)
    if r1 is not None and r2 is not None:
        return name1 if r1 >= r2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2

def _power(name, stats):
    s = _lookup(name, stats)
    if not s:
        return None
    srs = s.get("srs", 0)
    away_w = s.get("wins_visitor", 0)
    away_l = s.get("losses_visitor", 1)
    away_pct = away_w / max(away_w + away_l, 1)
    return srs + (away_pct - 0.5) * 5
'''

# Algo C: SRS + strength of schedule penalty for weak-conference teams
algo_sos_penalty = CORE + '''
def _pick(name1, seed1, name2, seed2, round_num, all_stats):
    r1 = _power(name1, all_stats)
    r2 = _power(name2, all_stats)
    if r1 is not None and r2 is not None:
        return name1 if r1 >= r2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2

def _power(name, stats):
    s = _lookup(name, stats)
    if not s:
        return None
    srs = s.get("srs", 0)
    sos = s.get("sos", s.get("sos_all", 0))
    # Penalize teams from weak conferences (low SOS)
    # Average SOS is ~0, strong conferences have SOS > 8
    sos_bonus = max(0, sos - 5) * 0.3
    return srs + sos_bonus
'''

# Algo D: Multi-stat composite with diminishing returns on SRS
algo_diminishing = CORE + '''
import math

def _pick(name1, seed1, name2, seed2, round_num, all_stats):
    r1 = _power(name1, all_stats)
    r2 = _power(name2, all_stats)
    if r1 is not None and r2 is not None:
        return name1 if r1 >= r2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2

def _power(name, stats):
    s = _lookup(name, stats)
    if not s:
        return None
    srs = s.get("srs", 0)
    off = s.get("off_rtg", 100)
    sos = s.get("sos", s.get("sos_all", 0))
    efg = s.get("efg_pct", 0.45)
    if efg > 1: efg = efg / 100
    # Diminishing returns: sqrt transformation on SRS
    srs_adj = math.copysign(math.sqrt(abs(srs)), srs) * 4
    return srs_adj + (off - 100) * 0.2 + sos * 0.15 + (efg - 0.45) * 20
'''

# Algo E: Stepped threshold model
algo_threshold = CORE + '''
def _pick(name1, seed1, name2, seed2, round_num, all_stats):
    s1 = _lookup(name1, all_stats)
    s2 = _lookup(name2, all_stats)
    srs1 = s1.get("srs", 0) if s1 else 0
    srs2 = s2.get("srs", 0) if s2 else 0
    sd1 = seed1 or 8
    sd2 = seed2 or 8

    srs_diff = srs1 - srs2
    seed_diff = sd2 - sd1  # positive = team1 better seed

    # Strong SRS advantage: always pick stats leader
    if abs(srs_diff) > 8:
        return name1 if srs_diff > 0 else name2
    # Moderate SRS advantage: blend with seeds
    elif abs(srs_diff) > 3:
        combined = srs_diff * 0.8 + seed_diff * 1.5
        return name1 if combined >= 0 else name2
    # Close matchup: favor seeds
    else:
        combined = srs_diff * 0.4 + seed_diff * 2.5
        return name1 if combined >= 0 else name2
'''

# Algo F: Current algo but with round-specific performance scaling
algo_round_scale = original.replace(
    "perf_prob = 0.5 + (score_diff * 0.05)",
    """# Round-specific scaling: more aggressive in early rounds, conservative in late
        round_scales = {0: 0.06, 1: 0.05, 2: 0.04, 3: 0.03, 4: 0.02, 5: 0.02}
        scale = round_scales.get(round_num, 0.05)
        perf_prob = 0.5 + (score_diff * scale)"""
)

print(f"{'Algorithm':25s} {'Avg':>7s} {'2022':>6s} {'2023':>6s} {'2024':>6s} {'2025':>6s}")
print("-" * 70)

for name, code in [
    ("current", original),
    ("round_specific", algo_round_specific),
    ("road_warrior", algo_road_warrior),
    ("sos_penalty", algo_sos_penalty),
    ("diminishing_srs", algo_diminishing),
    ("threshold", algo_threshold),
    ("round_scale", algo_round_scale),
]:
    avg, yrs = test_algo(name, code)
    if avg:
        print(f"{name:25s} {avg:>7.1f} {yrs.get('2022','?'):>6} {yrs.get('2023','?'):>6} {yrs.get('2024','?'):>6} {yrs.get('2025','?'):>6}")
    else:
        print(f"{name:25s} FAILED")

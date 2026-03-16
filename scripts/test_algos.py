"""Test multiple algorithm approaches to find the best one."""
import json
import sys
import subprocess
import os

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
    print(f"  {name} FAILED: {r.stderr[:200]}")
    return None, None


LOOKUP_FN = '''
def _get_stat(name, stats, field):
    if not stats or not name:
        return None
    s = stats.get(name)
    if not s:
        nl = name.lower()
        for k, v in stats.items():
            if k.lower() == nl:
                s = v; break
        if not s:
            for k, v in stats.items():
                if nl in k.lower() or k.lower() in nl:
                    s = v; break
    return s.get(field) if s else None
'''

BRACKET_SCAFFOLD = '''
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

        winner = _pick_winner(name1, seed1, name2, seed2, round_num, team_stats)
        predictions.append({"game_id": game_id, "round_num": round_num, "predicted_winner": winner})
        advancing[game_id] = {"name": winner, "seed": seed1 if winner == name1 else seed2}
    return predictions
'''

# Algorithm: Pure SRS
pure_srs = BRACKET_SCAFFOLD + '''
def _pick_winner(name1, seed1, name2, seed2, round_num, stats):
    srs1 = _get_stat(name1, stats, "srs")
    srs2 = _get_stat(name2, stats, "srs")
    if srs1 is not None and srs2 is not None:
        return name1 if srs1 >= srs2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2
''' + LOOKUP_FN

# Algorithm: SRS with seed tiebreaker at various thresholds
def srs_seed_thresh(thresh):
    return BRACKET_SCAFFOLD + f'''
def _pick_winner(name1, seed1, name2, seed2, round_num, stats):
    srs1 = _get_stat(name1, stats, "srs")
    srs2 = _get_stat(name2, stats, "srs")
    if srs1 is not None and srs2 is not None:
        diff = srs1 - srs2
        if abs(diff) < {thresh}:
            return name1 if (seed1 or 16) <= (seed2 or 16) else name2
        return name1 if diff > 0 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2
''' + LOOKUP_FN

# Algorithm: SRS + off_rtg composite
srs_off = BRACKET_SCAFFOLD + '''
def _pick_winner(name1, seed1, name2, seed2, round_num, stats):
    r1 = _rating(name1, stats)
    r2 = _rating(name2, stats)
    if r1 is not None and r2 is not None:
        return name1 if r1 >= r2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2

def _rating(name, stats):
    srs = _get_stat(name, stats, "srs")
    off = _get_stat(name, stats, "off_rtg")
    if srs is None:
        return None
    bonus = ((off or 100) - 100) * 0.1
    return srs + bonus
''' + LOOKUP_FN

# Algorithm: SRS + win_loss_pct composite
srs_wl = BRACKET_SCAFFOLD + '''
def _pick_winner(name1, seed1, name2, seed2, round_num, stats):
    r1 = _rating(name1, stats)
    r2 = _rating(name2, stats)
    if r1 is not None and r2 is not None:
        return name1 if r1 >= r2 else name2
    return name1 if (seed1 or 16) <= (seed2 or 16) else name2

def _rating(name, stats):
    srs = _get_stat(name, stats, "srs")
    wl = _get_stat(name, stats, "win_loss_pct")
    if srs is None:
        return None
    bonus = ((wl or 0.5) - 0.5) * 10
    return srs + bonus
''' + LOOKUP_FN

# Algorithm: SRS with seed-weighted blend (seed matters for big mismatches)
srs_seed_blend = BRACKET_SCAFFOLD + '''
def _pick_winner(name1, seed1, name2, seed2, round_num, stats):
    srs1 = _get_stat(name1, stats, "srs")
    srs2 = _get_stat(name2, stats, "srs")
    s1 = seed1 or 8
    s2 = seed2 or 8
    if srs1 is not None and srs2 is not None:
        # SRS-based probability
        srs_diff = srs1 - srs2
        srs_prob = 0.5 + srs_diff * 0.03  # ~3% per SRS point
        srs_prob = max(0.05, min(0.95, srs_prob))
        # Seed-based probability
        seed_diff = s2 - s1  # positive means team1 has better seed
        seed_prob = 0.5 + seed_diff * 0.03
        seed_prob = max(0.05, min(0.95, seed_prob))
        # Blend: 80% SRS, 20% seed
        combined = 0.8 * srs_prob + 0.2 * seed_prob
        return name1 if combined >= 0.5 else name2
    return name1 if s1 <= s2 else name2
''' + LOOKUP_FN


print(f"{'Algorithm':25s} {'Avg':>7s} {'2022':>6s} {'2023':>6s} {'2024':>6s} {'2025':>6s}")
print("-" * 70)

for name, code in [
    ("current", original),
    ("pure_srs", pure_srs),
    ("srs_seed_t0", srs_seed_thresh(0)),
    ("srs_seed_t1", srs_seed_thresh(1)),
    ("srs_seed_t2", srs_seed_thresh(2)),
    ("srs_seed_t3", srs_seed_thresh(3)),
    ("srs_seed_t5", srs_seed_thresh(5)),
    ("srs+off_rtg", srs_off),
    ("srs+win_loss", srs_wl),
    ("srs_seed_blend", srs_seed_blend),
]:
    avg, yrs = test_algo(name, code)
    if avg:
        print(f"{name:25s} {avg:>7.1f} {yrs.get('2022','?'):>6} {yrs.get('2023','?'):>6} {yrs.get('2024','?'):>6} {yrs.get('2025','?'):>6}")

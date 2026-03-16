"""
March Madness Bracket Optimizer — Live Dashboard

Streamlit dashboard that auto-refreshes as the agent swarm optimizes predict.py.
Reads from dashboard_state.json (written by orchestrator) and runs scoring directly.

Usage:
    streamlit run dashboard.py
"""

import json
import os
import re
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
import altair as alt
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_STATE = os.path.join(PROJECT_DIR, "dashboard_state.json")
OLD_TESTS_MD = os.path.join(PROJECT_DIR, "docs", "old_tests.md")
PREDICT_PY = os.path.join(PROJECT_DIR, "predict.py")
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
BRACKETS_DIR = os.path.join(DATA_DIR, "brackets")

BASELINE_SCORE = 970.0
YEARS = [2022, 2023, 2024, 2025]

ROUND_NAMES = {
    0: "Round of 64",
    1: "Round of 32",
    2: "Sweet 16",
    3: "Elite 8",
    4: "Final Four",
    5: "Championship",
}

ROUND_PTS = {0: 10, 1: 20, 2: 40, 3: 80, 4: 160, 5: 320}

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="March Madness Optimizer",
    page_icon="🏀",  # user asked for emojis in UI context
    layout="wide",
)

# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _predict_mtime():
    try:
        return os.path.getmtime(PREDICT_PY)
    except OSError:
        return 0


def _state_mtime():
    try:
        return os.path.getmtime(DASHBOARD_STATE)
    except OSError:
        return 0


def load_dashboard_state():
    """Load the JSON state file written by the orchestrator."""
    try:
        with open(DASHBOARD_STATE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def run_fresh_test():
    """Run the test harness and return full results."""
    if sys.platform == "win32":
        python = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
    else:
        python = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
    if not os.path.exists(python):
        python = sys.executable

    run_test = os.path.join(SCRIPTS_DIR, "run_test.py")
    result = subprocess.run(
        [python, run_test, "--json"],
        capture_output=True, text=True, cwd=PROJECT_DIR,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return None


def parse_old_tests():
    """Parse docs/old_tests.md into a list of experiment dicts."""
    try:
        text = Path(OLD_TESTS_MD).read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    experiments = []
    blocks = re.split(r"(?=## Experiment #)", text)
    for block in blocks:
        m = re.match(
            r"## Experiment #(\d+)\s*(?:.|)\s*(PASS|FAIL|BASELINE)",
            block,
        )
        if not m:
            # Also handle the baseline entry
            m2 = re.match(r"## Experiment #(\d+)\s*(?:.|)\s*BASELINE", block)
            if m2:
                exp = {
                    "num": int(m2.group(1)),
                    "status": "BASELINE",
                    "score": _extract_field(block, "New Score"),
                    "change": _extract_field(block, "Change"),
                    "date": _extract_field(block, "Date"),
                }
                experiments.append(exp)
            continue

        exp_num = int(m.group(1))
        status = m.group(2)

        exp = {
            "num": exp_num,
            "status": status,
            "score": _extract_field(block, "New Score"),
            "baseline": _extract_field(block, "Baseline Score"),
            "change": _extract_field(block, "Change"),
            "date": _extract_field(block, "Date"),
        }
        experiments.append(exp)

    return experiments


def _extract_field(block, field_name):
    m = re.search(rf"- {field_name}:\s*(.+)", block)
    return m.group(1).strip() if m else ""


def get_git_score_history():
    """Parse git log for score progression."""
    result = subprocess.run(
        ["git", "log", "--oneline", "--reverse"],
        capture_output=True, text=True, cwd=PROJECT_DIR,
    )
    if result.returncode != 0:
        return []

    history = []
    for line in result.stdout.strip().splitlines():
        # Match: Experiment #N: ... (score: X -> Y)
        m = re.search(r"Experiment #(\d+):.*\(score:\s*([\d.]+)\s*->\s*([\d.]+)\)", line)
        if m:
            history.append({
                "experiment": int(m.group(1)),
                "old_score": float(m.group(2)),
                "new_score": float(m.group(3)),
                "passed": True,
            })
        # Match failed: Log experiment #N: ... [FAILED]
        m2 = re.search(r"Log experiment #(\d+):", line)
        if m2 and "[FAILED]" in line:
            history.append({
                "experiment": int(m2.group(1)),
                "old_score": None,
                "new_score": None,
                "passed": False,
            })

    return history


def load_bracket_predictions(year):
    """Run predictor on a single year and return per-game details."""
    if sys.platform == "win32":
        python = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
    else:
        python = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
    if not os.path.exists(python):
        python = sys.executable

    run_test = os.path.join(SCRIPTS_DIR, "run_test.py")
    result = subprocess.run(
        [python, run_test, "--json", "--year", str(year)],
        capture_output=True, text=True, cwd=PROJECT_DIR,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout.strip())
        return data.get("per_year", {}).get(str(year))
    except (json.JSONDecodeError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Swarm status indicator
# ---------------------------------------------------------------------------

def swarm_status():
    state = load_dashboard_state()
    if not state:
        return "grey", "Swarm not running"
    try:
        ts = datetime.fromisoformat(state["timestamp"])
        age = (datetime.now() - ts).total_seconds()
    except (KeyError, ValueError):
        return "grey", "Unknown"

    if age < 120:
        return "green", f"Active  --  Round {state.get('round_num', '?')}, Agent {state.get('agent_num', '?')}"
    elif age < 600:
        return "orange", f"Idle ({int(age)}s ago)"
    else:
        return "red", f"Stale ({int(age // 60)}m ago)"


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def main():
    # --- Sidebar ---
    with st.sidebar:
        st.title("Controls")

        color, status_text = swarm_status()
        color_dot = {"green": "🟢", "orange": "🟡", "red": "🔴", "grey": "⚪"}.get(color, "⚪")
        st.markdown(f"### {color_dot} {status_text}")

        refresh_interval = st.selectbox("Auto-refresh interval", [5, 10, 30, 60], index=1)
        if st.button("Refresh Now"):
            st.cache_data.clear()
            st.rerun()

        bracket_year = st.selectbox("Bracket year", YEARS, index=3)

        st.markdown("---")
        st.caption(f"Baseline: {BASELINE_SCORE}")
        state = load_dashboard_state()
        if state:
            st.caption(f"Attempts: {state.get('total_attempts', 0)}")
            st.caption(f"Improvements: {state.get('total_improvements', 0)}")

    # --- Auto-refresh via fragment ---
    _render_dashboard(refresh_interval, bracket_year)


@st.fragment(run_every=timedelta(seconds=10))
def _render_dashboard(refresh_interval, bracket_year):
    """Main dashboard content, auto-refreshes."""

    # Load data
    state = load_dashboard_state()
    test_results = _cached_test(int(_predict_mtime()))

    # =====================================================================
    # HERO METRICS
    # =====================================================================
    st.markdown("# March Madness Bracket Optimizer")

    if test_results and not test_results.get("error"):
        current_score = test_results["average_score"]
        per_year = test_results.get("per_year", {})
    elif state:
        current_score = state.get("current_score", 0)
        per_year = state.get("per_year", {})
    else:
        current_score = BASELINE_SCORE
        per_year = {}

    delta = current_score - BASELINE_SCORE

    col_main, col_2022, col_2023, col_2024, col_2025 = st.columns([2, 1, 1, 1, 1])
    with col_main:
        st.metric("Average Score", f"{current_score} / 1920",
                  delta=f"{delta:+.1f}" if delta != 0 else None)
    for col, yr in zip([col_2022, col_2023, col_2024, col_2025], YEARS):
        yr_data = per_year.get(str(yr), per_year.get(yr, {}))
        yr_score = yr_data.get("total_score", "?") if isinstance(yr_data, dict) else "?"
        with col:
            st.metric(str(yr), f"{yr_score}")

    # =====================================================================
    # TABS
    # =====================================================================
    tab_overview, tab_experiments, tab_algorithm, tab_bracket = st.tabs(
        ["Overview", "Experiments", "Algorithm", "Bracket"]
    )

    # ----- Overview Tab -----
    with tab_overview:
        _render_overview(test_results, per_year)

    # ----- Experiments Tab -----
    with tab_experiments:
        _render_experiments()

    # ----- Algorithm Tab -----
    with tab_algorithm:
        _render_algorithm()

    # ----- Bracket Tab -----
    with tab_bracket:
        _render_bracket(bracket_year)


@st.cache_data(ttl=15)
def _cached_test(predict_mtime):
    """Cache test results, keyed on predict.py mtime."""
    return run_fresh_test()


def _render_overview(test_results, per_year):
    """Per-round breakdown and score progression chart."""

    # --- Per-round breakdown ---
    st.subheader("Per-Round Breakdown")

    if test_results and "avg_by_round" in test_results:
        avg_rounds = test_results["avg_by_round"]
        rows = []
        for r in range(6):
            rd = avg_rounds.get(str(r), avg_rounds.get(r, {}))
            if not rd:
                continue
            correct = rd.get("correct", 0)
            total = rd.get("total", 0)
            pts = rd.get("points", 0)
            max_pts = rd.get("max_points", 0)
            pct = f"{correct/total*100:.0f}%" if total > 0 else "-"
            rows.append({
                "Round": ROUND_NAMES[r],
                "Correct": f"{correct}/{total}",
                "Points": f"{pts}/{max_pts}",
                "Accuracy": pct,
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Run the test suite to see per-round breakdown.")

    # --- Per-year detail ---
    st.subheader("Per-Year Detail")
    if test_results and "per_year" in test_results:
        year_tabs = st.tabs([str(y) for y in YEARS])
        for tab, yr in zip(year_tabs, YEARS):
            with tab:
                yr_data = test_results["per_year"].get(str(yr), test_results["per_year"].get(yr))
                if yr_data and "by_round" in yr_data:
                    rows = []
                    for r in range(6):
                        rd = yr_data["by_round"].get(str(r), yr_data["by_round"].get(r, {}))
                        if not rd:
                            continue
                        rows.append({
                            "Round": ROUND_NAMES[r],
                            "Correct": f"{rd.get('correct',0)}/{rd.get('total',0)}",
                            "Points": f"{rd.get('points',0)}/{rd.get('max_points',0)}",
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    st.metric("Total", f"{yr_data.get('total_score', '?')} / 1920")

    # --- Score progression chart ---
    st.subheader("Score Progression")
    history = get_git_score_history()
    experiments = parse_old_tests()

    if history:
        # Build progression from git history
        df = pd.DataFrame(history)
        passed_df = df[df["passed"]].copy()
        if not passed_df.empty:
            chart = alt.Chart(passed_df).mark_line(point=True, color="#22c55e").encode(
                x=alt.X("experiment:Q", title="Experiment #"),
                y=alt.Y("new_score:Q", title="Score", scale=alt.Scale(zero=False)),
                tooltip=["experiment", "old_score", "new_score"],
            )
            baseline_rule = alt.Chart(
                pd.DataFrame({"y": [BASELINE_SCORE]})
            ).mark_rule(strokeDash=[5, 5], color="grey").encode(y="y:Q")
            st.altair_chart(chart + baseline_rule, use_container_width=True)
        else:
            st.info("No improvements yet.")
    elif len(experiments) > 1:
        # Fallback: build from old_tests.md
        scores = []
        running_score = BASELINE_SCORE
        for exp in experiments:
            score_str = exp.get("score", "")
            m = re.match(r"([\d.]+)", score_str)
            if m:
                s = float(m.group(1))
                if exp.get("status") == "PASS":
                    running_score = s
                scores.append({"experiment": exp["num"], "score": running_score,
                               "status": exp.get("status", "")})
        if scores:
            df = pd.DataFrame(scores)
            chart = alt.Chart(df).mark_line(point=True).encode(
                x="experiment:Q",
                y=alt.Y("score:Q", scale=alt.Scale(zero=False)),
                color=alt.Color("status:N",
                                scale=alt.Scale(domain=["PASS", "FAIL", "BASELINE"],
                                                range=["#22c55e", "#ef4444", "#6b7280"])),
            )
            st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No experiments yet. Start the swarm to see score progression.")


def _render_experiments():
    """Show the experiment history table."""
    st.subheader("Experiment History")
    experiments = parse_old_tests()

    if not experiments:
        st.info("No experiments logged yet.")
        return

    rows = []
    for exp in reversed(experiments):  # newest first
        status = exp.get("status", "?")
        badge = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else status)
        rows.append({
            "#": exp.get("num", "?"),
            "Status": badge,
            "Score": exp.get("score", "?"),
            "Change": exp.get("change", ""),
            "Date": exp.get("date", ""),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.map(
            lambda v: "background-color: #dcfce7" if v == "PASS"
            else ("background-color: #fecaca" if v == "FAIL" else ""),
            subset=["Status"],
        ),
        use_container_width=True,
        hide_index=True,
    )


def _render_algorithm():
    """Show the current predict.py source."""
    st.subheader("Current Algorithm")
    try:
        mtime = datetime.fromtimestamp(_predict_mtime()).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last modified: {mtime}")
    except OSError:
        pass
    try:
        code = Path(PREDICT_PY).read_text(encoding="utf-8")
        st.code(code, language="python", line_numbers=True)
    except FileNotFoundError:
        st.error("predict.py not found")


def _render_bracket(year):
    """Show predicted vs actual bracket for a selected year."""
    st.subheader(f"Bracket Comparison  --  {year}")

    bracket_file = os.path.join(BRACKETS_DIR, f"bracket_{year}.json")
    if not os.path.exists(bracket_file):
        st.warning(f"No bracket data for {year}")
        return

    with open(bracket_file, "r", encoding="utf-8") as f:
        bracket = json.load(f)

    # Get predictions by running predictor
    sys.path.insert(0, PROJECT_DIR)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("predict", PREDICT_PY)
        predict_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(predict_mod)

        stats_file = os.path.join(DATA_DIR, "team_stats", f"stats_{year}.json")
        team_stats = {}
        if os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                team_stats = json.load(f)

        predictions = predict_mod.predict_bracket(bracket, team_stats)
    except Exception as e:
        st.error(f"Error running predictor: {e}")
        return

    # Build lookup: game_id -> predicted_winner
    pred_map = {p["game_id"]: p["predicted_winner"] for p in predictions}

    # Show round by round
    games = sorted(bracket["games"], key=lambda g: (g["round_num"], g["game_id"]))

    for round_num in range(6):
        round_games = [g for g in games if g["round_num"] == round_num]
        if not round_games:
            continue

        st.markdown(f"**{ROUND_NAMES[round_num]}** ({ROUND_PTS[round_num]} pts each)")

        rows = []
        for g in round_games:
            gid = g["game_id"]
            t1 = g["team1"]
            t2 = g["team2"]
            actual = g.get("winner", "?")
            predicted = pred_map.get(gid, "?")

            # Fuzzy match for correct check
            correct = _names_match(predicted, actual)

            rows.append({
                "Game": gid,
                "Matchup": f"({t1['seed']}) {t1['name']}  vs  ({t2['seed']}) {t2['name']}",
                "Predicted": predicted,
                "Actual": actual,
                "Result": "Correct" if correct else "Wrong",
            })

        df = pd.DataFrame(rows)
        st.dataframe(
            df.style.map(
                lambda v: "background-color: #dcfce7" if v == "Correct"
                else ("background-color: #fecaca" if v == "Wrong" else ""),
                subset=["Result"],
            ),
            use_container_width=True,
            hide_index=True,
        )


def _names_match(n1, n2):
    """Simple fuzzy name match."""
    if not n1 or not n2:
        return False
    n1, n2 = n1.strip().lower(), n2.strip().lower()
    if n1 == n2:
        return True
    if len(n1) > 4 and len(n2) > 4:
        if n1 in n2 or n2 in n1:
            return True
    return False


if __name__ == "__main__":
    main()

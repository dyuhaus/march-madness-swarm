"""
Test runner for the March Madness bracket predictor.

Runs predict.py against all 4 historical brackets (2022-2025),
scores each one, and returns the average score.

This is the evaluation harness — the "fixed 5-minute training run"
equivalent from autoresearch. The metric is average ESPN score across
all 4 years. Higher is better. Max is 1,920.

Usage:
    python scripts/run_test.py
    python scripts/run_test.py --verbose
    python scripts/run_test.py --year 2023
"""

import json
import os
import sys
import argparse
import importlib.util
import traceback

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from scorer import score_bracket, format_scorecard

YEARS = [2022, 2023, 2024, 2025]
DATA_DIR = os.path.join(PROJECT_DIR, "data")
BRACKETS_DIR = os.path.join(DATA_DIR, "brackets")
STATS_DIR = os.path.join(DATA_DIR, "team_stats")


def load_json(filepath):
    """Load a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_predictor():
    """
    Dynamically load predict.py from the project root.
    This ensures we always get the latest version even if it's been modified.
    """
    predict_path = os.path.join(PROJECT_DIR, "predict.py")
    if not os.path.exists(predict_path):
        print(f"ERROR: predict.py not found at {predict_path}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location("predict", predict_path)
    predict_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predict_module)
    
    if not hasattr(predict_module, "predict_bracket"):
        print("ERROR: predict.py must define a predict_bracket(bracket, team_stats) function")
        sys.exit(1)
    
    return predict_module


def run_single_year(predict_module, year, verbose=False):
    """
    Run the predictor on a single year and return the score result.
    
    Returns:
        dict: Score result from scorer.score_bracket(), or None if error
    """
    bracket_file = os.path.join(BRACKETS_DIR, f"bracket_{year}.json")
    stats_file = os.path.join(STATS_DIR, f"stats_{year}.json")
    
    if not os.path.exists(bracket_file):
        print(f"  WARNING: No bracket data for {year}, skipping.")
        return None
    
    bracket = load_json(bracket_file)
    
    # Check if bracket has actual games
    if not bracket.get("games") or len(bracket["games"]) == 0:
        print(f"  WARNING: Bracket for {year} has no games, skipping.")
        return None
    
    # Load team stats (optional — predictor should handle missing stats)
    team_stats = {}
    if os.path.exists(stats_file):
        team_stats = load_json(stats_file)
    
    # Run the predictor
    try:
        predictions = predict_module.predict_bracket(bracket, team_stats)
    except Exception as e:
        print(f"  ERROR running predictor for {year}: {e}")
        if verbose:
            traceback.print_exc()
        return None
    
    if not predictions:
        print(f"  WARNING: Predictor returned no predictions for {year}")
        return None
    
    # Score the predictions
    result = score_bracket(predictions, bracket["games"])
    result["year"] = year
    
    return result


def run_all_years(verbose=False, single_year=None):
    """
    Run the predictor on all years (or a single year) and return results.
    
    Returns:
        dict with:
            - average_score: float
            - per_year: dict of year -> score result
            - years_tested: int
            - error: str or None
    """
    predict_module = load_predictor()
    
    years_to_test = [single_year] if single_year else YEARS
    results = {}
    
    for year in years_to_test:
        if verbose:
            print(f"\n{'='*50}")
            print(f"  Testing year {year}")
            print(f"{'='*50}")
        
        result = run_single_year(predict_module, year, verbose)
        if result:
            results[year] = result
            if verbose:
                print(f"\n{format_scorecard(result)}")
    
    if not results:
        return {
            "average_score": 0,
            "per_year": {},
            "years_tested": 0,
            "error": "No valid test results"
        }
    
    # Calculate average
    total = sum(r["total_score"] for r in results.values())
    avg = total / len(results)
    
    # Average by round
    avg_by_round = {}
    for r in range(6):
        round_correct = sum(res["by_round"][r]["correct"] for res in results.values())
        round_total = sum(res["by_round"][r]["total"] for res in results.values())
        round_points = sum(res["by_round"][r]["points"] for res in results.values())
        round_max = sum(res["by_round"][r]["max_points"] for res in results.values())
        
        avg_by_round[r] = {
            "correct": round_correct,
            "total": round_total,
            "points": round_points,
            "max_points": round_max,
        }
    
    return {
        "average_score": round(avg, 1),
        "total_across_years": total,
        "per_year": results,
        "years_tested": len(results),
        "avg_by_round": avg_by_round,
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser(description="Run March Madness bracket predictor tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed results")
    parser.add_argument("--year", "-y", type=int, help="Test a single year only")
    parser.add_argument("--json", action="store_true", help="Output as JSON (for orchestrator)")
    args = parser.parse_args()
    
    if args.year and args.year not in YEARS:
        print(f"ERROR: Year must be one of {YEARS}")
        sys.exit(1)
    
    results = run_all_years(verbose=args.verbose, single_year=args.year)
    
    if args.json:
        # Machine-readable output for the orchestrator
        # Strip details to keep it compact
        output = {
            "average_score": results["average_score"],
            "years_tested": results["years_tested"],
            "error": results["error"],
            "per_year": {}
        }
        for year, res in results["per_year"].items():
            output["per_year"][year] = {
                "total_score": res["total_score"],
                "correct_picks": res["correct_picks"],
                "total_picks": res["total_picks"],
            }
        print(json.dumps(output))
    else:
        # Human-readable output
        print("\n" + "=" * 60)
        print("  MARCH MADNESS BRACKET OPTIMIZER — TEST RESULTS")
        print("=" * 60)
        
        if results["error"]:
            print(f"\n  ERROR: {results['error']}")
            sys.exit(1)
        
        for year, res in sorted(results["per_year"].items()):
            print(f"\n--- {year} ---")
            print(format_scorecard(res))
        
        print(f"\n{'='*60}")
        print(f"  AVERAGE SCORE: {results['average_score']} / 1920")
        print(f"  Years tested: {results['years_tested']}")
        print(f"{'='*60}")
    
    # Return the average score as exit code hint (0 = success)
    sys.exit(0 if results["average_score"] > 0 else 1)


if __name__ == "__main__":
    main()

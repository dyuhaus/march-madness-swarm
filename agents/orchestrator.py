"""
March Madness Bracket Optimizer — Swarm Orchestrator

Runs a sequential loop of 5 agents per round. Each agent:
1. Reads program.md, old_tests.md, problem.md, and current predict.py
2. Calls the Claude API to decide on a change
3. Applies the change to predict.py
4. Runs the test suite (scripts/run_test.py)
5. If improved → git commit + update logs
6. If not improved → git reset + log failure

Inspired by karpathy/autoresearch: the human writes program.md,
the agents write the code, the metric decides what stays.

Usage:
    python agents/orchestrator.py                    # Run indefinitely
    python agents/orchestrator.py --rounds 10        # Run 10 rounds (50 agent attempts)
    python agents/orchestrator.py --rounds 1         # Run 1 round (5 agent attempts)
    python agents/orchestrator.py --dry-run          # Show what would happen, don't execute

Environment:
    ANTHROPIC_API_KEY must be set (or in .env file)
"""

import os
import sys
import json
import subprocess
import argparse
import time
from datetime import datetime

# Project paths
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(AGENT_DIR)
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

PREDICT_PY = os.path.join(PROJECT_DIR, "predict.py")
PROGRAM_MD = os.path.join(DOCS_DIR, "program.md")
OLD_TESTS_MD = os.path.join(DOCS_DIR, "old_tests.md")
PROBLEM_MD = os.path.join(DOCS_DIR, "problem.md")
RUN_TEST = os.path.join(PROJECT_DIR, "scripts", "run_test.py")

AGENTS_PER_ROUND = 5
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
DASHBOARD_STATE = os.path.join(PROJECT_DIR, "dashboard_state.json")

# Determine python executable
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(PROJECT_DIR, ".venv", "bin", "python")

if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable  # Fallback to current Python


def write_dashboard_state(current_score, per_year, round_num, agent_num,
                          total_attempts, total_improvements, last_exp=None):
    """Write dashboard state for the Streamlit UI to pick up."""
    state = {
        "timestamp": datetime.now().isoformat(),
        "current_score": current_score,
        "round_num": round_num,
        "agent_num": agent_num,
        "total_attempts": total_attempts,
        "total_improvements": total_improvements,
        "per_year": per_year,
        "last_experiment": last_exp,
    }
    tmp = DASHBOARD_STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, DASHBOARD_STATE)


def read_file(path):
    """Read a text file and return contents."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[File not found: {path}]"


def write_file(path, content):
    """Write content to a text file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_cmd(cmd, cwd=None, capture=True):
    """Run a shell command and return result."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or PROJECT_DIR,
        capture_output=capture, text=True
    )
    return result


def get_current_score():
    """Run the test suite and return the score as a dict."""
    result = run_cmd(f'"{VENV_PYTHON}" "{RUN_TEST}" --json')
    if result.returncode != 0:
        print(f"  Test run failed: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"  Could not parse test output: {result.stdout[:200]}")
        return None


def git_commit(message):
    """Stage all changes and commit."""
    run_cmd("git add -A")
    run_cmd(f'git commit -m "{message}"')


def git_push():
    """Push to remote."""
    run_cmd("git push")


def git_reset_hard():
    """Reset all changes to last commit."""
    run_cmd("git checkout -- .")


def git_get_diff():
    """Get the current diff of predict.py."""
    result = run_cmd(f'git diff "{PREDICT_PY}"')
    return result.stdout if result.returncode == 0 else ""


def get_experiment_count():
    """Count how many experiments have been logged."""
    content = read_file(OLD_TESTS_MD)
    return content.count("## Experiment #")


def call_claude_api(system_prompt, user_prompt):
    """
    Call the Anthropic API to get agent's proposed change.
    
    Returns the response text, or None on error.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        return None
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Try loading from .env
        env_file = os.path.join(PROJECT_DIR, ".env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"')
                        break
    
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Set it as environment variable or in .env file.")
        return None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"  API call failed: {e}")
        return None


def build_agent_prompt(agent_num, baseline_score, baseline_details):
    """
    Build the system and user prompts for an agent.
    """
    program = read_file(PROGRAM_MD)
    old_tests = read_file(OLD_TESTS_MD)
    problem = read_file(PROBLEM_MD)
    current_predict = read_file(PREDICT_PY)
    
    system_prompt = f"""You are Agent #{agent_num} in a swarm optimization loop for a March Madness bracket predictor.

Your job: make ONE targeted change to predict.py that improves the average ESPN bracket score.

CRITICAL RULES:
1. Output ONLY the complete new predict.py file content, wrapped in ```python and ``` markers.
2. Before the code block, write a brief description (2-3 sentences) of what you're changing and why.
3. After the code block, write a brief "PROBLEM_UPDATE" section with any new knowledge to add to problem.md.
4. Do NOT repeat changes that have already been tried (check the experiment log).
5. The predict_bracket(bracket, team_stats) function signature and return format MUST stay the same.
6. Do NOT use game["winner"] or any actual results in prediction logic.

RESPONSE FORMAT:
CHANGE: <brief description of what and why>

```python
<complete predict.py file>
```

PROBLEM_UPDATE: <new knowledge to add to problem.md, or "None" if no new insights>
"""
    
    user_prompt = f"""## Current State

**Baseline average score: {baseline_score} / 1920**

Per-year breakdown:
{json.dumps(baseline_details, indent=2)}

## Program Instructions (READ ONLY)
{program}

## Previous Experiments
{old_tests}

## Accumulated Knowledge
{problem}

## Current predict.py (the file you will modify)
```python
{current_predict}
```

Now propose your ONE change. Remember:
- Check old_tests.md to avoid duplicates
- Focus on changes most likely to improve the AVERAGE across all 4 years
- Later rounds are worth more — prioritize Final Four / Championship accuracy
- Output the COMPLETE predict.py file, not just a diff
"""
    
    return system_prompt, user_prompt


def parse_agent_response(response_text):
    """
    Parse the agent's response to extract:
    - change_description: what was changed
    - new_predict_py: the complete new file
    - problem_update: new knowledge for problem.md
    """
    change_desc = ""
    new_code = ""
    problem_update = ""
    
    # Extract change description
    if "CHANGE:" in response_text:
        change_start = response_text.index("CHANGE:") + len("CHANGE:")
        code_start = response_text.find("```python")
        if code_start > change_start:
            change_desc = response_text[change_start:code_start].strip()
    
    # Extract code block
    if "```python" in response_text and "```" in response_text:
        code_start = response_text.index("```python") + len("```python")
        # Find the closing ``` after the opening ```python
        remaining = response_text[code_start:]
        code_end = remaining.find("```")
        if code_end > 0:
            new_code = remaining[:code_end].strip()
    
    # Extract problem update
    if "PROBLEM_UPDATE:" in response_text:
        pu_start = response_text.index("PROBLEM_UPDATE:") + len("PROBLEM_UPDATE:")
        problem_update = response_text[pu_start:].strip()
    
    return change_desc, new_code, problem_update


def log_experiment(exp_num, agent_num, passed, change_desc, 
                   baseline_score, new_score, baseline_details, new_details,
                   problem_update):
    """Append an experiment entry to old_tests.md."""
    status = "PASS" if passed else "FAIL"
    change = new_score - baseline_score if new_score else 0
    sign = "+" if change >= 0 else ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    entry = f"""
## Experiment #{exp_num} — {status}
- Agent: agent-{agent_num}
- Date: {now}
- Baseline Score: {baseline_score}
- New Score: {new_score} ({sign}{change:.1f})
- Change: {change_desc}
"""
    
    # Per-year breakdown
    if new_details and baseline_details:
        entry += "- Per-Year Breakdown:\n"
        for year in sorted(set(list(baseline_details.keys()) + list(new_details.keys()))):
            old_yr = baseline_details.get(str(year), baseline_details.get(int(year), {}))
            new_yr = new_details.get(str(year), new_details.get(int(year), {}))
            old_s = old_yr.get("total_score", "?") if isinstance(old_yr, dict) else "?"
            new_s = new_yr.get("total_score", "?") if isinstance(new_yr, dict) else "?"
            entry += f"  - {year}: {old_s} → {new_s}\n"
    
    # Analysis
    if passed:
        entry += f"- Analysis: Score improved by {change:.1f} points. "
        if problem_update and problem_update.lower() != "none":
            entry += f"{problem_update}\n"
        else:
            entry += "No additional insights.\n"
    else:
        entry += f"- Analysis: Score did not improve (change: {sign}{change:.1f}). "
        if problem_update and problem_update.lower() != "none":
            entry += f"{problem_update}\n"
        else:
            entry += "Change was not beneficial.\n"
    
    # Append to old_tests.md
    current = read_file(OLD_TESTS_MD)
    write_file(OLD_TESTS_MD, current + "\n" + entry)


def update_problem_md(problem_update):
    """Append new knowledge to problem.md."""
    if not problem_update or problem_update.lower() == "none":
        return
    
    current = read_file(PROBLEM_MD)
    
    # Find the right section to append to
    if "## Discovered Relationships" in current:
        # Append before "## Open Questions"
        if "## Open Questions" in current:
            parts = current.split("## Open Questions")
            updated = parts[0].rstrip() + f"\n\n- {problem_update}\n\n## Open Questions" + parts[1]
        else:
            updated = current + f"\n\n- {problem_update}\n"
    else:
        updated = current + f"\n\n## New Learnings\n\n- {problem_update}\n"
    
    write_file(PROBLEM_MD, updated)


def run_agent(agent_num, round_num, baseline_score, baseline_details, dry_run=False):
    """
    Run a single agent's optimization attempt.
    
    Returns:
        tuple: (passed: bool, new_score: float or None)
    """
    exp_num = get_experiment_count() + 1
    
    print(f"\n{'-'*60}")
    print(f"  Round {round_num}, Agent {agent_num} (Experiment #{exp_num})")
    print(f"  Baseline: {baseline_score} / 1920")
    print(f"{'-'*60}")
    
    # Step 1: Build prompt
    print("  [1/5] Building prompt...")
    system_prompt, user_prompt = build_agent_prompt(
        agent_num, baseline_score, baseline_details
    )
    
    if dry_run:
        print("  [DRY RUN] Would call Claude API here.")
        return False, None
    
    # Step 2: Call Claude API
    print("  [2/5] Calling Claude API for proposed change...")
    response = call_claude_api(system_prompt, user_prompt)
    
    if not response:
        print("  SKIP: API call failed.")
        return False, None
    
    # Step 3: Parse response and apply change
    print("  [3/5] Parsing response and applying change...")
    change_desc, new_code, problem_update = parse_agent_response(response)
    
    if not new_code:
        print("  SKIP: Could not parse code from response.")
        print(f"  Response preview: {response[:300]}...")
        log_experiment(exp_num, agent_num, False, "Failed to parse response",
                      baseline_score, None, baseline_details, None, None)
        return False, None
    
    if not change_desc:
        change_desc = "Unspecified change"
    
    print(f"  Change: {change_desc[:100]}")
    
    # Save current predict.py as backup
    backup = read_file(PREDICT_PY)
    
    # Write new predict.py
    write_file(PREDICT_PY, new_code)
    
    # Step 4: Run tests
    print("  [4/5] Running tests on all 4 years...")
    test_result = get_current_score()
    
    if not test_result or test_result.get("error"):
        error_msg = test_result.get("error", "Unknown error") if test_result else "Test crashed"
        print(f"  ERROR: {error_msg}")
        # Revert
        write_file(PREDICT_PY, backup)
        log_experiment(exp_num, agent_num, False, 
                      f"{change_desc} [CRASHED: {error_msg}]",
                      baseline_score, 0, baseline_details, None, problem_update)
        return False, None
    
    new_score = test_result["average_score"]
    new_details = test_result.get("per_year", {})
    
    # Step 5: Keep or revert
    print(f"  [5/5] Score: {new_score} (baseline: {baseline_score})")
    
    if new_score > baseline_score:
        # IMPROVEMENT! Commit it.
        print(f"  IMPROVEMENT: +{new_score - baseline_score:.1f} points!")
        
        log_experiment(exp_num, agent_num, True, change_desc,
                      baseline_score, new_score, baseline_details, new_details,
                      problem_update)
        update_problem_md(problem_update)
        
        git_commit(f"Experiment #{exp_num}: {change_desc[:50]} (score: {baseline_score} -> {new_score})")
        git_push()

        return True, new_score
    else:
        # No improvement, revert
        print(f"  No improvement ({new_score} <= {baseline_score}). Reverting.")

        write_file(PREDICT_PY, backup)

        log_experiment(exp_num, agent_num, False, change_desc,
                      baseline_score, new_score, baseline_details, new_details,
                      problem_update)

        # Still commit the log update
        git_commit(f"Log experiment #{exp_num}: {change_desc[:50]} [FAILED]")
        git_push()

        return False, None


def main():
    parser = argparse.ArgumentParser(description="March Madness Bracket Optimizer Swarm")
    parser.add_argument("--rounds", type=int, default=0, 
                       help="Number of rounds (0 = run until stopped)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would happen without making changes")
    parser.add_argument("--agents", type=int, default=AGENTS_PER_ROUND,
                       help=f"Agents per round (default: {AGENTS_PER_ROUND})")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  March Madness Bracket Optimizer — Swarm Orchestrator")
    print("=" * 60)
    print(f"  Agents per round: {args.agents}")
    print(f"  Rounds: {'unlimited' if args.rounds == 0 else args.rounds}")
    print(f"  Model: {MODEL}")
    print(f"  Dry run: {args.dry_run}")
    
    # Get initial baseline
    print("\nEstablishing baseline...")
    baseline_result = get_current_score()
    
    if not baseline_result or baseline_result.get("error"):
        print(f"ERROR: Could not establish baseline: {baseline_result}")
        print("Make sure data/ is populated. Run: python scripts/scrape_data.py")
        sys.exit(1)
    
    baseline_score = baseline_result["average_score"]
    baseline_details = baseline_result.get("per_year", {})
    
    print(f"Baseline score: {baseline_score} / 1920")
    for year, yr_result in sorted(baseline_details.items()):
        if isinstance(yr_result, dict):
            print(f"  {year}: {yr_result.get('total_score', '?')}")

    write_dashboard_state(baseline_score, baseline_details, 0, 0, 0, 0)

    # Main loop
    round_num = 0
    total_improvements = 0
    total_attempts = 0
    
    try:
        while True:
            round_num += 1
            
            if args.rounds > 0 and round_num > args.rounds:
                break
            
            print(f"\n{'='*60}")
            print(f"  ROUND {round_num}")
            print(f"  Current best: {baseline_score} / 1920")
            print(f"  Improvements so far: {total_improvements}/{total_attempts}")
            print(f"{'='*60}")
            
            for agent_num in range(1, args.agents + 1):
                total_attempts += 1
                
                passed, new_score = run_agent(
                    agent_num, round_num, 
                    baseline_score, baseline_details,
                    dry_run=args.dry_run
                )
                
                last_exp = {
                    "exp_num": get_experiment_count(),
                    "passed": passed,
                    "old_score": baseline_score,
                    "new_score": new_score,
                }

                if passed and new_score is not None:
                    total_improvements += 1
                    baseline_score = new_score
                    # Refresh baseline details
                    fresh = get_current_score()
                    if fresh and not fresh.get("error"):
                        baseline_details = fresh.get("per_year", {})

                write_dashboard_state(
                    baseline_score, baseline_details, round_num, agent_num,
                    total_attempts, total_improvements, last_exp
                )

                # Brief pause between agents to avoid API rate limits
                if not args.dry_run:
                    time.sleep(2)
            
            print(f"\n  Round {round_num} complete.")
            print(f"  Score: {baseline_score} / 1920")
            print(f"  Total improvements: {total_improvements}/{total_attempts}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"  SWARM COMPLETE")
    print(f"{'='*60}")
    print(f"  Rounds completed: {round_num}")
    print(f"  Total attempts: {total_attempts}")
    print(f"  Improvements: {total_improvements}")
    print(f"  Final score: {baseline_score} / 1920")
    print(f"  Success rate: {total_improvements/total_attempts*100:.1f}%" if total_attempts > 0 else "  No attempts made")


if __name__ == "__main__":
    main()

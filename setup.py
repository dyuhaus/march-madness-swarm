"""
One-time setup script for the March Madness Bracket Optimizer.

This script:
1. Creates a Python virtual environment
2. Installs dependencies
3. Creates a new GitHub repository
4. Makes the initial commit
5. Runs the data scraper to populate data/
6. Runs the baseline test

Usage:
    python setup.py
"""

import subprocess
import sys
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_NAME = "march-madness-swarm"


def run(cmd, check=True, capture=False, cwd=None):
    """Run a shell command and print it."""
    print(f"  > {cmd}")
    result = subprocess.run(
        cmd, shell=True, check=check, cwd=cwd or PROJECT_DIR,
        capture_output=capture, text=True
    )
    return result


def main():
    print("=" * 60)
    print("  March Madness Bracket Optimizer — Setup")
    print("=" * 60)

    # --- Step 1: Virtual environment ---
    print("\n[1/6] Creating virtual environment...")
    venv_path = os.path.join(PROJECT_DIR, ".venv")
    if not os.path.exists(venv_path):
        run(f"{sys.executable} -m venv .venv")
    else:
        print("  Virtual environment already exists, skipping.")

    # Determine pip path
    if sys.platform == "win32":
        pip = os.path.join(venv_path, "Scripts", "pip.exe")
        python = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip = os.path.join(venv_path, "bin", "pip")
        python = os.path.join(venv_path, "bin", "python")

    # --- Step 2: Install dependencies ---
    print("\n[2/6] Installing dependencies...")
    run(f'"{pip}" install -r requirements.txt')

    # --- Step 3: Initialize git ---
    print("\n[3/6] Initializing git repository...")
    if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
        run("git init")
        run("git add -A")
        run('git commit -m "Initial project scaffold"')
    else:
        print("  Git already initialized, skipping.")

    # --- Step 4: Create GitHub repo ---
    print("\n[4/6] Creating GitHub repository...")
    # Check if remote already exists
    result = run("git remote get-url origin", check=False, capture=True)
    if result.returncode != 0:
        print(f"  Creating repo: {REPO_NAME}")
        run(f'gh repo create {REPO_NAME} --public --source=. --push')
    else:
        print(f"  Remote already set: {result.stdout.strip()}")

    # --- Step 5: Scrape data ---
    print("\n[5/6] Scraping historical bracket and team data...")
    print("  This may take a few minutes on first run.")
    run(f'"{python}" scripts/scrape_data.py')

    # Commit the data
    run("git add data/")
    result = run('git diff --cached --quiet', check=False)
    if result.returncode != 0:
        run('git commit -m "Add historical bracket and team data (2022-2025)"')
        run("git push")

    # --- Step 6: Run baseline ---
    print("\n[6/6] Running baseline test...")
    run(f'"{python}" scripts/run_test.py')

    # Commit baseline results to old_tests.md
    run("git add -A")
    result = run('git diff --cached --quiet', check=False)
    if result.returncode != 0:
        run('git commit -m "Baseline score established"')
        run("git push")

    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("  Run the swarm with: python agents/orchestrator.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

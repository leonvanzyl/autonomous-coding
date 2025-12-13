"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
"""

import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path


WEBHOOK_URL = os.environ.get("PROGRESS_N8N_WEBHOOK_URL")
PROGRESS_CACHE_FILE = ".progress_cache"


def send_progress_webhook(passing: int, total: int, project_dir: Path) -> None:
    """Send webhook notification when progress increases."""
    if not WEBHOOK_URL:
        return  # Webhook not configured

    cache_file = project_dir / PROGRESS_CACHE_FILE
    previous = 0
    previous_passing_tests = set()

    # Read previous progress and passing test indices
    if cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text())
            previous = cache_data.get("count", 0)
            previous_passing_tests = set(cache_data.get("passing_indices", []))
        except:
            previous = 0

    # Only notify if progress increased
    if passing > previous:
        # Find which tests are now passing
        tests_file = project_dir / "feature_list.json"
        completed_tests = []
        current_passing_indices = []

        if tests_file.exists():
            try:
                with open(tests_file, "r") as f:
                    tests = json.load(f)
                for i, test in enumerate(tests):
                    if test.get("passes", False):
                        current_passing_indices.append(i)
                        if i not in previous_passing_tests:
                            # This test is newly passing
                            desc = test.get("description", f"Test #{i+1}")
                            category = test.get("category", "")
                            if category:
                                completed_tests.append(f"[{category}] {desc}")
                            else:
                                completed_tests.append(desc)
            except:
                pass

        payload = {
            "event": "test_progress",
            "passing": passing,
            "total": total,
            "percentage": round((passing / total) * 100, 1) if total > 0 else 0,
            "previous_passing": previous,
            "tests_completed_this_session": passing - previous,
            "completed_tests": completed_tests,
            "project": project_dir.name,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps([payload]).encode('utf-8'),  # n8n expects array
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"[Webhook notification failed: {e}]")

        # Update cache with count and passing indices
        cache_file.write_text(json.dumps({
            "count": passing,
            "passing_indices": current_passing_indices
        }))
    else:
        # Update cache even if no change (for initial state)
        if not cache_file.exists():
            tests_file = project_dir / "feature_list.json"
            current_passing_indices = []
            if tests_file.exists():
                try:
                    with open(tests_file, "r") as f:
                        tests = json.load(f)
                    for i, test in enumerate(tests):
                        if test.get("passes", False):
                            current_passing_indices.append(i)
                except:
                    pass
            cache_file.write_text(json.dumps({
                "count": passing,
                "passing_indices": current_passing_indices
            }))


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    tests_file = project_dir / "feature_list.json"

    if not tests_file.exists():
        return 0, 0

    try:
        with open(tests_file, "r") as f:
            tests = json.load(f)

        total = len(tests)
        passing = sum(1 for test in tests if test.get("passes", False))

        return passing, total
    except (json.JSONDecodeError, IOError):
        return 0, 0


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_tests(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        print(f"\nProgress: {passing}/{total} tests passing ({percentage:.1f}%)")
        send_progress_webhook(passing, total, project_dir)
    else:
        print("\nProgress: feature_list.json not yet created")

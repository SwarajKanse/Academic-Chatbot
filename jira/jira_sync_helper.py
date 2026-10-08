#!/usr/bin/env python3
"""
Jira Agile Lifecycle & Sprint Management CLI Helper
Facilitates DevOps pipeline synchronization with Jira Software boards and Smart Commits.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any


def load_agile_metadata(filepath: str = "jira/jira_agile_sprint_lifecycle.json") -> Dict[str, Any]:
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def display_board(data: Dict[str, Any]):
    print("=" * 80)
    print(f" JIRA AGILE BOARD - PROJECT: {data['project']['key']} ({data['project']['name']})")
    print("=" * 80)

    print("\n[ACTIVE SPRINTS]")
    for sprint in data.get("sprints", []):
        status_flag = "ACTIVE" if sprint["state"] == "ACTIVE" else "CLOSED"
        print(f" * {sprint['name']} [{status_flag}]")
        print(f"   Goal: {sprint['goal']}")

    print("\n[TEAM MEMBERS & COLLABORATION]")
    for member in data.get("team_members", []):
        print(f" * {member['name']} <{member['email']}> - {member['role']}")

    print("\n[USER STORIES & ISSUE TRACKER]")
    print(f"{'Key':<10} | {'Status':<10} | {'Points':<7} | {'Assignee':<26} | {'Summary'}")
    print("-" * 80)
    for issue in data.get("issues", []):
        assignee_short = issue['assignee'].split('@')[0]
        print(f"{issue['key']:<10} | {issue['status']:<10} | {issue['storyPoints']:<7} | {assignee_short:<26} | {issue['summary'][:32]}")
    print("=" * 80)


def validate_commit_message(msg: str) -> bool:
    """Validates if commit message contains a valid Jira ticket like [ACAD-101]."""
    import re
    match = re.search(r"\[ACAD-\d+\]", msg)
    if not match:
        print("ERROR: Commit message must reference a valid Jira issue key: [ACAD-XXX]")
        return False
    print(f"PASSED: Commit message references Jira ticket {match.group(0)}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Jira Agile & DevOps Pipeline Integration Helper")
    parser.add_argument("--board", action="store_true", help="Display full Agile Sprint Board")
    parser.add_argument("--validate-commit", type=str, help="Validate commit message against Jira Smart Commit schema")
    parser.add_argument("--summary", action="store_true", help="Print sprint velocity and story point totals")

    args = parser.parse_args()
    data = load_agile_metadata()

    if args.board:
        display_board(data)
    elif args.validate_commit:
        if not validate_commit_message(args.validate_commit):
            sys.exit(1)
    elif args.summary:
        total_points = sum(i.get("storyPoints", 0) for i in data.get("issues", []))
        done_points = sum(i.get("storyPoints", 0) for i in data.get("issues", []) if i.get("status") == "Done")
        print(f"Total Story Points: {total_points}")
        print(f"Completed Story Points: {done_points} ({(done_points/total_points)*100:.1f}%)")
    else:
        display_board(data)


if __name__ == "__main__":
    main()

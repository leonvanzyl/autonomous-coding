#!/usr/bin/env python3
"""
Simple CLI launcher for the Autonomous Coding Agent.
Provides an interactive menu to create new projects or continue existing ones.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_existing_projects() -> list[str]:
    """Get list of existing projects from generations folder."""
    generations_dir = Path("generations")
    if not generations_dir.exists():
        return []

    projects = []
    for item in generations_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            projects.append(item.name)

    return sorted(projects)


def display_menu(projects: list[str]) -> None:
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("  Autonomous Coding Agent Launcher")
    print("=" * 50)
    print("\n[1] Create new project")

    if projects:
        print("[2] Continue existing project")

    print("[q] Quit")
    print()


def display_projects(projects: list[str]) -> None:
    """Display list of existing projects."""
    print("\n" + "-" * 40)
    print("  Existing Projects")
    print("-" * 40)

    for i, project in enumerate(projects, 1):
        print(f"  [{i}] {project}")

    print("\n  [b] Back to main menu")
    print()


def get_project_choice(projects: list[str]) -> str | None:
    """Get user's project selection."""
    while True:
        choice = input("Select project number: ").strip().lower()

        if choice == 'b':
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                return projects[idx]
            print(f"Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("Invalid input. Enter a number or 'b' to go back.")


def get_new_project_name() -> str | None:
    """Get name for new project."""
    print("\n" + "-" * 40)
    print("  Create New Project")
    print("-" * 40)
    print("\nEnter project name (e.g., my-awesome-app)")
    print("Leave empty to cancel.\n")

    name = input("Project name: ").strip()

    if not name:
        return None

    # Basic validation
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        if char in name:
            print(f"Invalid character '{char}' in project name")
            return None

    return name


def run_agent(project_name: str) -> None:
    """Run the autonomous agent with the given project."""
    print(f"\nStarting agent for project: {project_name}")
    print("-" * 50)

    # Build the command
    cmd = [sys.executable, "autonomous_agent_demo.py", "--project-dir", project_name]

    # Run the agent
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("\n\nAgent interrupted. Run again to resume.")


def main() -> None:
    """Main entry point."""
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    while True:
        projects = get_existing_projects()
        display_menu(projects)

        choice = input("Select option: ").strip().lower()

        if choice == 'q':
            print("\nGoodbye!")
            break

        elif choice == '1':
            project_name = get_new_project_name()
            if project_name:
                run_agent(project_name)

        elif choice == '2' and projects:
            display_projects(projects)
            selected = get_project_choice(projects)
            if selected:
                run_agent(selected)

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()

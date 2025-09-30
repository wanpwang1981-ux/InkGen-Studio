# -*- coding: utf-8 -*-
"""
InkGen Studio - Main Command-Line Interface (CLI)
==================================================

This script serves as the main entry point for interacting with the
InkGen Studio application from the command line. It delegates all
complex logic to the Orchestrator.

Author: Jules
Date: 2025-09-30
Version: 1.1 (Refactored)
"""

import argparse
import os
from orchestrator import Orchestrator

def handle_create_persona(args, orchestrator):
    """CLI handler for the 'create-persona' command."""
    print("--- InkGen Studio: Create Persona ---")
    for path in args.samples:
        if not os.path.exists(path):
            print(f"Error: Sample file not found at '{path}'"); return
    if args.extra and not os.path.exists(args.extra):
        print(f"Error: Extra materials file not found at '{args.extra}'"); return

    try:
        orchestrator.run_create_persona(args.author, args.samples, args.output, args.extra)
    except Exception as e:
        print(f"\nAn error occurred during persona creation: {e}")

def handle_create_outline(args, orchestrator):
    """CLI handler for the 'create-outline' command."""
    print("--- InkGen Studio: Create Novel Outline ---")
    if args.persona and not os.path.exists(args.persona):
        print(f"Error: Persona file not found at '{args.persona}'"); return

    try:
        orchestrator.run_create_outline(args.title, args.output, args.chapters, args.persona)
    except Exception as e:
        print(f"\nAn error occurred during outline creation: {e}")

def handle_init_project(args, orchestrator):
    """CLI handler for the 'init' command."""
    if not os.path.exists(args.outline):
        print(f"Error: Outline file not found at '{args.outline}'"); return
    if args.persona and not os.path.exists(args.persona):
        print(f"Error: Persona file not found at '{args.persona}'"); return

    try:
        orchestrator.run_init_project(args.title, args.outline, args.persona, args.output_dir)
    except Exception as e:
        print(f"\nAn error occurred during project initialization: {e}")

def handle_generate_novel(args, orchestrator):
    """CLI handler for the 'generate-novel' command."""
    print("--- InkGen Studio: Generate Novel Chapters ---")
    project_path = args.project
    if not os.path.exists(project_path) or not os.path.isdir(project_path) or not os.path.exists(os.path.join(project_path, "project.json")):
        print(f"Error: Project directory '{project_path}' is not valid or does not contain a project.json file."); return

    try:
        orchestrator.run_generate_novel(project_path, args.max_revisions)
    except Exception as e:
        print(f"\nAn error occurred during novel generation: {e}")

def main():
    """Main function to parse CLI arguments and dispatch commands."""
    parser = argparse.ArgumentParser(description="InkGen Studio: AI-powered writing assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- 'init' command ---
    parser_init = subparsers.add_parser("init", help="Initialize a new novel project directory.")
    parser_init.add_argument("--title", type=str, required=True, help="The title of the new novel.")
    parser_init.add_argument("--outline", type=str, required=True, help="Path to the JSON story outline file.")
    parser_init.add_argument("--persona", type=str, help="Optional path to a JSON persona profile.")
    parser_init.add_argument("--output-dir", type=str, default="novels/", help="Base directory to create the project in (default: 'novels/').")
    parser_init.set_defaults(func=handle_init_project)

    # --- 'create-persona' command ---
    parser_persona = subparsers.add_parser("create-persona", help="Create a new writer persona.")
    parser_persona.add_argument("--author", type=str, required=True, help="Name of the author to create a persona for.")
    parser_persona.add_argument("--samples", type=str, nargs='+', required=True, help="Path(s) to text samples of the author's work.")
    parser_persona.add_argument("--extra", type=str, help="Optional path to extra materials (interviews, etc.).")
    parser_persona.add_argument("--output", type=str, required=True, help="Path to save the generated JSON persona profile.")
    parser_persona.set_defaults(func=handle_create_persona)

    # --- 'create-outline' command ---
    parser_outline = subparsers.add_parser("create-outline", help="Create a new novel outline.")
    parser_outline.add_argument("--title", type=str, required=True, help="Title or core theme of the novel.")
    parser_outline.add_argument("--persona", type=str, help="Optional path to a JSON persona profile.")
    parser_outline.add_argument("--chapters", type=int, default=10, help="Target number of chapters (default: 10).")
    parser_outline.add_argument("--output", type=str, required=True, help="Path to save the generated JSON outline.")
    parser_outline.set_defaults(func=handle_create_outline)

    # --- 'generate-novel' command ---
    parser_generate = subparsers.add_parser("generate-novel", help="Generate novel chapters from a project.")
    parser_generate.add_argument("--project", type=str, required=True, help="Path to the project directory containing project.json.")
    parser_generate.add_argument("--max-revisions", type=int, default=2, help="Maximum number of revisions per chapter (default: 2).")
    parser_generate.set_defaults(func=handle_generate_novel)

    args = parser.parse_args()

    orchestrator = Orchestrator()
    args.func(args, orchestrator)

if __name__ == "__main__":
    main()
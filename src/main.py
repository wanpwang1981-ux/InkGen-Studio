# -*- coding: utf-8 -*-
"""
InkGen Studio - Main Command-Line Interface (CLI)
==================================================

This script serves as the main entry point for interacting with the
InkGen Studio application from the command line.

It provides commands to access the various functionalities of the system,
starting with the creation of writer personas.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

import argparse
import json
import os
from agents.persona_architect import PersonaArchitect
from agents.lead_architect import LeadArchitect

def create_persona(args):
    """
    Handler for the 'create-persona' command.
    """
    print("--- InkGen Studio: Create Persona ---")

    author_name = args.author
    sample_paths = args.samples
    output_path = args.output

    for path in sample_paths:
        if not os.path.exists(path):
            print(f"Error: Sample file not found at '{path}'")
            return

    text_samples = []
    print(f"Reading {len(sample_paths)} sample file(s)...")
    for path in sample_paths:
        with open(path, 'r', encoding='utf-8') as f:
            text_samples.append(f.read())

    extra_materials = ""
    if args.extra:
        if not os.path.exists(args.extra):
            print(f"Error: Extra materials file not found at '{args.extra}'")
            return
        print(f"Reading extra materials from '{args.extra}'...")
        with open(args.extra, 'r', encoding='utf-8') as f:
            extra_materials = f.read()

    try:
        from config import config
        print(f"Found {len(config.api_keys)} API key(s).")
        architect = PersonaArchitect()
        persona_profile = architect.run(
            author_name=author_name,
            text_samples=text_samples,
            other_materials=extra_materials
        )
    except (ValueError, Exception) as e:
        print(f"\nAn error occurred during persona creation: {e}")
        return

    print(f"Saving generated persona profile to '{output_path}'...")
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(persona_profile, f, ensure_ascii=False, indent=2)
        print(f"\nPersona creation successful! Profile saved to '{output_path}'")
    except IOError as e:
        print(f"Error: Could not write to output file '{output_path}'. Reason: {e}")

def create_outline(args):
    """
    Handler for the 'create-outline' command.
    """
    print("--- InkGen Studio: Create Novel Outline ---")

    persona_data = None
    if args.persona:
        print(f"Loading persona from '{args.persona}'...")
        if not os.path.exists(args.persona):
            print(f"Error: Persona file not found at '{args.persona}'")
            return
        with open(args.persona, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)

    try:
        from config import config
        print(f"Found {len(config.api_keys)} API key(s).")
        architect = LeadArchitect(persona=persona_data)
        story_outline = architect.run(
            novel_title=args.title,
            num_chapters=args.chapters
        )
    except (ValueError, Exception) as e:
        print(f"\nAn error occurred during outline creation: {e}")
        return

    print(f"Saving generated outline to '{args.output}'...")
    try:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(story_outline, f, ensure_ascii=False, indent=2)
        print(f"\nOutline creation successful! Outline saved to '{args.output}'")
    except IOError as e:
        print(f"Error: Could not write to output file '{args.output}'. Reason: {e}")

def main():
    """
    Main function to parse command-line arguments and dispatch commands.
    """
    parser = argparse.ArgumentParser(
        description="InkGen Studio: AI-powered writing assistant for web novels."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- 'create-persona' command ---
    parser_persona = subparsers.add_parser(
        "create-persona",
        help="Create a new writer persona from sample texts."
    )
    parser_persona.add_argument("--author", type=str, required=True, help="The name of the author to create a persona for.")
    parser_persona.add_argument("--samples", type=str, nargs='+', required=True, help="One or more file paths to text samples of the author's work.")
    parser_persona.add_argument("--extra", type=str, help="Optional file path to extra materials (interviews, analysis, etc.).")
    parser_persona.add_argument("--output", type=str, required=True, help="The file path to save the generated JSON persona profile.")
    parser_persona.set_defaults(func=create_persona)

    # --- 'create-outline' command ---
    parser_outline = subparsers.add_parser(
        "create-outline",
        help="Create a new novel outline using a title and optional persona."
    )
    parser_outline.add_argument("--title", type=str, required=True, help="The title or core theme of the novel.")
    parser_outline.add_argument("--persona", type=str, help="Optional file path to a JSON persona profile to guide the style.")
    parser_outline.add_argument("--chapters", type=int, default=10, help="The target number of chapters for the outline (default: 10).")
    parser_outline.add_argument("--output", type=str, required=True, help="The file path to save the generated JSON outline.")
    parser_outline.set_defaults(func=create_outline)

    # --- Parse arguments and call the corresponding function ---
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
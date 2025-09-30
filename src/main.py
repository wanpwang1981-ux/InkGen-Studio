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

def create_persona(args):
    """
    Handler for the 'create-persona' command.

    This function orchestrates the process of creating a new writer persona
    by reading input files, invoking the PersonaArchitect agent, and saving
    the resulting profile.
    """
    print("--- InkGen Studio: Create Persona ---")

    # --- 1. Input Validation and File Reading ---
    author_name = args.author
    sample_paths = args.samples
    output_path = args.output

    # Validate that all sample files exist
    for path in sample_paths:
        if not os.path.exists(path):
            print(f"Error: Sample file not found at '{path}'")
            return

    # Read text samples
    text_samples = []
    print(f"Reading {len(sample_paths)} sample file(s)...")
    for path in sample_paths:
        with open(path, 'r', encoding='utf-8') as f:
            text_samples.append(f.read())

    # Read extra materials if provided
    extra_materials = ""
    if args.extra:
        if not os.path.exists(args.extra):
            print(f"Error: Extra materials file not found at '{args.extra}'")
            return
        print(f"Reading extra materials from '{args.extra}'...")
        with open(args.extra, 'r', encoding='utf-8') as f:
            extra_materials = f.read()

    # --- 2. Invoke the Agent ---
    try:
        # Before running the agent, ensure API keys are set.
        # The config module will raise an error if not, which we catch here.
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

    # --- 3. Save the Output ---
    print(f"Saving generated persona profile to '{output_path}'...")
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(persona_profile, f, ensure_ascii=False, indent=2)

        print("\nPersona creation successful!")
        print(f"Profile for '{author_name}' saved to '{output_path}'")

    except IOError as e:
        print(f"Error: Could not write to output file '{output_path}'. Reason: {e}")


def main():
    """
    Main function to parse command-line arguments and dispatch commands.
    """
    parser = argparse.ArgumentParser(
        description="InkGen Studio: AI-powered writing assistant for web novels."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- 'create-persona' command ---
    parser_create = subparsers.add_parser(
        "create-persona",
        help="Create a new writer persona from sample texts."
    )
    parser_create.add_argument(
        "--author",
        type=str,
        required=True,
        help="The name of the author to create a persona for (e.g., 'Ni Kuang')."
    )
    parser_create.add_argument(
        "--samples",
        type=str,
        nargs='+',  # Allows one or more sample files
        required=True,
        help="One or more file paths to text samples of the author's work."
    )
    parser_create.add_argument(
        "--extra",
        type=str,
        help="Optional file path to extra materials (interviews, analysis, etc.)."
    )
    parser_create.add_argument(
        "--output",
        type=str,
        required=True,
        help="The file path to save the generated JSON persona profile (e.g., 'personas/ni_kuang.json')."
    )
    parser_create.set_defaults(func=create_persona)

    # --- Parse arguments and call the corresponding function ---
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    # To run this from the root directory: python -m src.main create-persona ...
    main()
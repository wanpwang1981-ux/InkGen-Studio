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
import re
from agents.persona_architect import PersonaArchitect
from agents.lead_architect import LeadArchitect
from agents.writer import Writer

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

from agents.refiner import Refiner
from agents.reader import Reader

from agents.refiner import Refiner
from agents.reader import Reader

def generate_novel(args):
    """
    Handler for the 'generate-novel' command.
    This function orchestrates the full pipeline, including the revision loop.
    """
    print("--- InkGen Studio: Generate Novel Chapters ---")

    # 1. Load Outline and Persona
    if not os.path.exists(args.outline):
        print(f"Error: Outline file not found at '{args.outline}'"); return
    with open(args.outline, 'r', encoding='utf-8') as f:
        story_outline = json.load(f)

    persona_data = None
    if args.persona:
        if not os.path.exists(args.persona):
            print(f"Error: Persona file not found at '{args.persona}'"); return
        with open(args.persona, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)

    # 2. Setup output directories
    novel_title = story_outline.get("novel_title", "Untitled Novel")
    safe_title = re.sub(r'[^\w\s-]', '', novel_title).strip().replace(' ', '_')
    base_output_dir = os.path.join(args.output_dir, safe_title)
    chapters_dir = os.path.join(base_output_dir, "chapters")
    reviews_dir = os.path.join(base_output_dir, "reviews")
    os.makedirs(chapters_dir, exist_ok=True)
    os.makedirs(reviews_dir, exist_ok=True)
    print(f"Output will be saved to '{base_output_dir}'")

    # 3. Instantiate Agents and generate chapters
    try:
        from config import config
        writer = Writer(persona=persona_data)
        refiner = Refiner(persona=persona_data)
        reader = Reader(persona=persona_data)

        context = f"Main Plot: {story_outline.get('main_plot', '')}\nCore Concepts: {story_outline.get('core_concepts', '')}"

        for chapter_outline in story_outline.get("chapters", []):
            chapter_number = chapter_outline.get("chapter_number")
            chapter_title = chapter_outline.get("title", f"Chapter {chapter_number}")
            print(f"\n--- Processing Chapter {chapter_number}: {chapter_title} ---")

            # --- The Self-Correction Loop ---
            revision_count = 0
            # First attempt
            draft_text = writer.run(chapter_outline=chapter_outline, context=context)
            refined_text = refiner.run(draft_text=draft_text)
            review_result = reader.run(refined_text=refined_text, chapter_outline=chapter_outline)

            # Revision loop if needed
            while review_result.get("status") == "revision_needed" and revision_count < args.max_revisions:
                revision_count += 1
                print(f"--- Revision Attempt {revision_count}/{args.max_revisions} for Chapter {chapter_number} ---")
                feedback = review_result.get("feedback", "No specific feedback provided.")
                print(f"Reader feedback: {feedback}")

                draft_text = writer.run(chapter_outline=chapter_outline, context=context, revision_feedback=feedback)
                refined_text = refiner.run(draft_text=draft_text)
                review_result = reader.run(refined_text=refined_text, chapter_outline=chapter_outline)

            if review_result.get("status") == "revision_needed":
                print(f"Warning: Chapter {chapter_number} was not approved after {args.max_revisions} revisions. Saving the last version.")
            else:
                print(f"Chapter {chapter_number} approved after {revision_count} revision(s).")
            # --- End of Loop ---

            # Save the final outputs
            safe_chapter_title = re.sub(r'[^\w\s-]', '', chapter_title).strip().replace(' ', '_')
            chapter_filename = f"{chapter_number:02d}_{safe_chapter_title}.txt"
            chapter_filepath = os.path.join(chapters_dir, chapter_filename)
            print(f"Saving final chapter text to '{chapter_filepath}'...")
            with open(chapter_filepath, 'w', encoding='utf-8') as f: f.write(refined_text)

            review_filename = f"{chapter_number:02d}_{safe_chapter_title}_review.json"
            review_filepath = os.path.join(reviews_dir, review_filename)
            print(f"Saving final review to '{review_filepath}'...")
            with open(review_filepath, 'w', encoding='utf-8') as f: json.dump(review_result, f, ensure_ascii=False, indent=2)

            context = f"Summary of previous chapter ({chapter_title}): {chapter_outline.get('summary', '')}"

        print(f"\nNovel generation complete! Output saved in '{base_output_dir}'")

    except (ValueError, Exception) as e:
        print(f"\nAn error occurred during novel generation: {e}")
        return

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

    # --- 'generate-novel' command ---
    parser_generate = subparsers.add_parser(
        "generate-novel",
        help="Generate a full novel draft from an outline file."
    )
    parser_generate.add_argument("--outline", type=str, required=True, help="File path to the JSON story outline.")
    parser_generate.add_argument("--persona", type=str, help="Optional file path to a JSON persona profile.")
    parser_generate.add_argument("--output-dir", type=str, default="novels/", help="The directory to save the generated novel chapters (default: 'novels/').")
    parser_generate.add_argument("--max-revisions", type=int, default=2, help="The maximum number of revisions per chapter (default: 2).")
    parser_generate.set_defaults(func=generate_novel)

    # --- Parse arguments and call the corresponding function ---
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
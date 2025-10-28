# -*- coding: utf-8 -*-
"""
InkGen Studio - Orchestrator
============================

This module contains the Orchestrator class, which is responsible for managing
the high-level workflows of the application, such as creating personas,
outlines, and generating entire novels.

It separates the core business logic from the command-line interface.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

import os
import json
import re
from tqdm import tqdm

from .agents.persona_architect import PersonaArchitect
from .agents.lead_architect import LeadArchitect
from .agents.writer import Writer
from .agents.refiner import Refiner
from .agents.reader import Reader
from .agents.info_extractor import InfoExtractor
from .knowledge_base_manager import KnowledgeBaseManager
from .config import config

class Orchestrator:
    """
    Manages and coordinates the AI agents to perform complex tasks.
    """

    def __init__(self):
        """
        Initializes the Orchestrator.
        """
        print("Orchestrator initialized. Ready to manage AI agent workflows.")

    def run_init_project(self, title: str, outline_path: str, persona_path: str, output_dir_base: str):
        """Initializes a new novel project."""
        print(f"Initializing new project: {title}")
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        project_dir = os.path.join(output_dir_base, safe_title)

        if os.path.exists(project_dir):
            print(f"Error: Project directory '{project_dir}' already exists.")
            return

        os.makedirs(project_dir)

        project_config = {
            "novel_title": title,
            "safe_title": safe_title,
            "status": "initialized",
            "outline_file": os.path.abspath(outline_path),
            "persona_file": os.path.abspath(persona_path) if persona_path else None,
            "chapters_dir": os.path.join(project_dir, "chapters"),
            "reviews_dir": os.path.join(project_dir, "reviews"),
            "knowledge_base_id": safe_title,
            "chapters_generated": 0
        }

        config_path = os.path.join(project_dir, "project.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(project_config, f, ensure_ascii=False, indent=2)

        print(f"Project '{title}' initialized successfully at '{project_dir}'")
        print(f"Configuration saved to '{config_path}'")

    def run_create_persona(self, author_name: str, sample_paths: list, output_path: str, extra_materials_path: str = None):
        text_samples = []
        for path in sample_paths:
            with open(path, 'r', encoding='utf-8') as f: text_samples.append(f.read())

        extra_materials = ""
        if extra_materials_path:
            with open(extra_materials_path, 'r', encoding='utf-8') as f: extra_materials = f.read()

        architect = PersonaArchitect()
        persona_profile = architect.run(
            author_name=author_name, text_samples=text_samples, other_materials=extra_materials
        )

        output_dir = os.path.dirname(output_path)
        if output_dir: os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(persona_profile, f, ensure_ascii=False, indent=2)
        print(f"\nPersona creation successful! Profile saved to '{output_path}'")

    def run_create_outline(self, title: str, output_path: str, chapters: int, persona_path: str = None):
        persona_data = None
        if persona_path:
            with open(persona_path, 'r', encoding='utf-8') as f: persona_data = json.load(f)

        architect = LeadArchitect(persona=persona_data)
        story_outline = architect.run(novel_title=title, num_chapters=chapters)

        output_dir = os.path.dirname(output_path)
        if output_dir: os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(story_outline, f, ensure_ascii=False, indent=2)
        print(f"\nOutline creation successful! Outline saved to '{output_path}'")

    def run_generate_novel(self, project_path: str, max_revisions: int):
        """Orchestrates the project-driven novel generation workflow."""
        config_path = os.path.join(project_path, "project.json")
        if not os.path.exists(config_path):
            print(f"Error: Project config file not found at '{config_path}'")
            return

        with open(config_path, 'r', encoding='utf-8') as f:
            project_config = json.load(f)

        # Load all necessary data from the project config
        outline_path = project_config["outline_file"]
        persona_path = project_config["persona_file"]
        chapters_dir = project_config["chapters_dir"]
        reviews_dir = project_config["reviews_dir"]
        kb_id = project_config["knowledge_base_id"]

        with open(outline_path, 'r', encoding='utf-8') as f: story_outline = json.load(f)

        persona_data = None
        if persona_path and os.path.exists(persona_path):
            with open(persona_path, 'r', encoding='utf-8') as f: persona_data = json.load(f)

        # Ensure output directories exist
        os.makedirs(chapters_dir, exist_ok=True)
        os.makedirs(reviews_dir, exist_ok=True)

        # Instantiate all necessary components
        kb_manager = KnowledgeBaseManager(novel_id=kb_id)
        writer = Writer(persona=persona_data)
        refiner = Refiner(persona=persona_data)
        reader = Reader(persona=persona_data)
        info_extractor = InfoExtractor()

        # The initial context is based on the overall plot and concepts
        short_term_context = f"Main Plot: {story_outline.get('main_plot', '')}\nCore Concepts: {story_outline.get('core_concepts', '')}"

        chapters = story_outline.get("chapters", [])
        for chapter_outline in tqdm(chapters, desc="Generating Chapters"):
            chapter_number = chapter_outline.get("chapter_number")
            chapter_title = chapter_outline.get("title", f"Chapter {chapter_number}")

            # 1. Query KB for long-term context
            query_text = f"Information relevant to: {chapter_outline.get('summary', '')}"
            relevant_knowledge = kb_manager.query(query_text)
            knowledge_context = "\n\n--- RELEVANT KNOWLEDGE FROM PREVIOUS CHAPTERS ---\n" + "\n".join(relevant_knowledge) if relevant_knowledge else ""
            full_context = f"{knowledge_context}\n\n--- PREVIOUS CHAPTER SUMMARY ---\n{short_term_context}"

            # 2. Run the self-correction loop
            revision_count = 0
            # First attempt
            draft_text = writer.run(chapter_outline=chapter_outline, context=full_context)
            refined_text = refiner.run(draft_text=draft_text)
            review_result = reader.run(refined_text=refined_text, chapter_outline=chapter_outline)

            # Revision loop
            while review_result.get("status") == "revision_needed" and revision_count < max_revisions:
                revision_count += 1
                feedback = review_result.get("feedback", "No specific feedback provided.")
                draft_text = writer.run(chapter_outline=chapter_outline, context=full_context, revision_feedback=feedback)
                refined_text = refiner.run(draft_text=draft_text)
                review_result = reader.run(refined_text=refined_text, chapter_outline=chapter_outline)

            # 3. Update KB if approved
            if review_result.get("status") == "approved":
                new_facts = info_extractor.run(text_to_analyze=refined_text)
                if new_facts: kb_manager.add(documents=new_facts)

            # 4. Save artifacts
            safe_chapter_title = re.sub(r'[^\w\s-]', '', chapter_title).strip().replace(' ', '_')
            chapter_filename = f"{chapter_number:02d}_{safe_chapter_title}.txt"
            with open(os.path.join(chapters_dir, chapter_filename), 'w', encoding='utf-8') as f: f.write(refined_text)

            review_filename = f"{chapter_number:02d}_{safe_chapter_title}_review.json"
            with open(os.path.join(reviews_dir, review_filename), 'w', encoding='utf-8') as f: json.dump(review_result, f, ensure_ascii=False, indent=2)

            # 5. Update short-term context for next iteration
            short_term_context = f"Summary of previous chapter ({chapter_title}): {chapter_outline.get('summary', '')}"

        print(f"\nNovel generation complete! Output saved in '{project_path}'")
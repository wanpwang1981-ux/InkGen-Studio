# -*- coding: utf-8 -*-
"""
InkGen Studio - Lead Architect Agent
====================================

This module contains the LeadArchitect class, the agent responsible for the
high-level planning of the novel.

It designs the story's backbone, including the main plot, core concepts,
and the chapter-by-chapter outline.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent
from typing import Dict, Any, List

class LeadArchitect(BaseAgent):
    """
    The agent responsible for macro-level story planning.

    This agent takes a core theme or title and generates the main plot points,
    world-building concepts, character summaries, and a detailed outline for
    all chapters.
    """

    def run(self, novel_title: str, num_chapters: int = 10) -> Dict[str, Any]:
        """
        Executes the planning process for the entire novel.

        Args:
            novel_title (str): The title or core theme of the novel.
            num_chapters (int): The target number of chapters for the outline.

        Returns:
            Dict[str, Any]: A dictionary containing the story's master plan.
        """
        import json

        print(f"LeadArchitect: Starting planning for novel '{novel_title}'...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_outline_prompt(novel_title, num_chapters)

        # 2. Call the LLM service
        print("LeadArchitect: Sending request to LLM for outline generation...")
        try:
            raw_response = self.llm_service.generate_text(task_prompt)
        except Exception as e:
            print(f"LeadArchitect: LLM call failed. Error: {e}")
            raise

        # 3. Parse the JSON response from the LLM
        print("LeadArchitect: Parsing LLM response...")
        try:
            clean_response = raw_response.strip().replace("```json", "").replace("```", "").strip()
            story_outline = json.loads(clean_response)
            print("LeadArchitect: Successfully parsed story outline.")
            return story_outline
        except json.JSONDecodeError as e:
            print(f"LeadArchitect: Failed to parse JSON from LLM response. Error: {e}")
            print(f"Raw response was:\n{raw_response}")
            raise ValueError("Failed to decode LLM response into valid JSON.") from e

    def _build_outline_prompt(self, novel_title: str, num_chapters: int) -> str:
        """
        Builds the detailed prompt for the LLM to generate a story outline.
        """
        prompt = f"""
You are a master storyteller and world-builder. Your task is to create a complete story outline for a web novel titled "{novel_title}".
The outline must be detailed, coherent, and follow the writing style defined by your current persona.
Your output MUST be a single, valid JSON object and nothing else.

Generate an outline with approximately {num_chapters} chapters.

The JSON object must have the following structure:
{{
  "novel_title": "{novel_title}",
  "main_plot": "A compelling, one-paragraph summary of the entire story arc, from beginning to end.",
  "core_concepts": {{
    "worldview": "A detailed description of the world, its rules, magic systems, or technology.",
    "main_character": "A description of the main character, including their motivations, flaws, and goals."
  }},
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "A creative title for the first chapter",
      "summary": "A detailed, one-paragraph summary of the events, character interactions, and plot progression in this chapter."
    }},
    {{
      "chapter_number": 2,
      "title": "A creative title for the second chapter",
      "summary": "A detailed, one-paragraph summary for this chapter."
    }}
  ]
}}

Ensure the "chapters" array contains an entry for every chapter up to {num_chapters}.
Remember, your entire response must be ONLY the JSON object.
"""
        # Use the BaseAgent's method to combine this task with the persona rules
        return self._construct_prompt(prompt)
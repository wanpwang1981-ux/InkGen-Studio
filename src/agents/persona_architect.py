# -*- coding: utf-8 -*-
"""
InkGen Studio - Persona Architect Agent
=======================================

This module contains the PersonaArchitect class, a specialized agent responsible
for creating persona profiles based on user-provided materials.

It's a "meta-agent" that doesn't write stories but creates the "souls"
for other agents to use.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent
from typing import List, Dict, Any

class PersonaArchitect(BaseAgent):
    """
    The agent responsible for creating new writer personas.

    This agent interacts with the user to gather information about a target
    author, analyzes the provided materials, and generates a structured
    persona file that can be used by other agents in the system.
    """

    def __init__(self):
        """
        Initializes the PersonaArchitect agent with a neutral, default persona,
        as its task is analytical and should not be stylized.
        """
        super().__init__() # Use the default persona for this agent

    def run(self, author_name: str, text_samples: List[str], other_materials: str = "") -> Dict[str, Any]:
        """
        Executes the persona creation process.

        Args:
            author_name (str): The name of the author to create a persona for.
            text_samples (List[str]): A list of strings, where each string is a
                                      significant text sample from the author.
            other_materials (str, optional): A string containing any additional
                                             context, like interviews or analysis.

        Returns:
            Dict[str, Any]: A dictionary representing the generated persona profile.
        """
        import json

        print(f"PersonaArchitect: Starting analysis for author '{author_name}'...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_analysis_prompt(author_name, text_samples, other_materials)

        # 2. Call the LLM service
        print("PersonaArchitect: Sending request to LLM for analysis...")
        try:
            raw_response = self.llm_service.generate_text(task_prompt)
        except Exception as e:
            print(f"PersonaArchitect: LLM call failed. Error: {e}")
            # Return an error structure or raise the exception
            raise

        # 3. Parse the JSON response from the LLM
        print("PersonaArchitect: Parsing LLM response...")
        try:
            # The LLM response might be enclosed in markdown backticks
            clean_response = raw_response.strip().replace("```json", "").replace("```", "").strip()
            persona_profile = json.loads(clean_response)
            print("PersonaArchitect: Successfully parsed persona profile.")
            return persona_profile
        except json.JSONDecodeError as e:
            print(f"PersonaArchitect: Failed to parse JSON from LLM response. Error: {e}")
            print(f"Raw response was:\n{raw_response}")
            # In a real app, we might retry or handle this more gracefully.
            # For now, we'll raise an error.
            raise ValueError("Failed to decode LLM response into valid JSON.") from e

    def _build_analysis_prompt(self, author_name: str, text_samples: List[str], other_materials: str) -> str:
        """
        Builds the detailed prompt for the LLM to analyze an author's style.
        """
        # Concatenate all text samples into a single block
        samples_text = "\n\n---\n\n".join(text_samples)

        # The instruction for the LLM is very specific, especially the JSON output format.
        prompt = f"""
You are an expert literary analyst. Your task is to create a "persona profile" for the author '{author_name}' based on the provided texts.
Your output MUST be a single, valid JSON object and nothing else. Do not add any explanatory text before or after the JSON.

The persona profile should capture the author's unique writing style, themes, and narrative techniques.
Analyze the following materials:

--- TEXT SAMPLES ---
{samples_text}
--- END TEXT SAMPLES ---

--- ADDITIONAL MATERIALS ---
{other_materials if other_materials else "None provided."}
--- END ADDITIONAL MATERIALS ---

Based on your analysis, generate a JSON object with the following structure:
{{
  "name": "{author_name}",
  "version": "1.0",
  "description": "A concise, one-sentence summary of the author's style and typical genre.",
  "rules": {{
    "narrative_style": {{
      "pacing": "Describe the typical pacing (e.g., 'fast-paced', 'leisurely').",
      "perspective": "Describe the common narrative perspective (e.g., 'first-person', 'third-person limited').",
      "hook": "Describe how the author typically begins stories or chapters."
    }},
    "dialogue_style": {{
      "length": "Describe the dialogue length (e.g., 'short and punchy', 'long and philosophical').",
      "function": "What is the primary function of dialogue (e.g., 'to advance plot', 'for character development')."
    }},
    "core_themes": [
      "List at least 3-5 core themes or recurring topics found in the author's work."
    ],
    "vocabulary_preferences": {{
      "common_words": ["List 5-10 characteristic words or phrases."],
      "forbidden_words": ["List words or concepts the author seems to avoid."]
    }},
    "structure": {{
      "chapter_ending": "Describe the typical style of chapter endings (e.g., 'cliffhanger', 'resolution')."
    }}
  }}
}}

Remember, your entire response must be ONLY the JSON object.
"""
        return self._construct_prompt(prompt)
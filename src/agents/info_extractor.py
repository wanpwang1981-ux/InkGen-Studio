# -*- coding: utf-8 -*-
"""
InkGen Studio - Info Extractor Agent
====================================

This module contains the InfoExtractor class, a specialized agent responsible
for reading a piece of text and extracting key, self-contained pieces of
information to be stored in a knowledge base.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent
from typing import List, Dict, Any
import json

class InfoExtractor(BaseAgent):
    """
    An agent specialized in extracting key information from text.

    Its goal is to identify and list factual statements about characters,
    locations, items, and lore that are crucial for maintaining story
    consistency.
    """

    def __init__(self):
        """
        Initializes the InfoExtractor with a neutral, default persona,
        as its task is purely analytical.
        """
        super().__init__()

    def run(self, text_to_analyze: str) -> List[str]:
        """
        Analyzes the given text and extracts key information as a list of facts.

        Args:
            text_to_analyze (str): The chapter text to be analyzed.

        Returns:
            List[str]: A list of self-contained factual statements.
                       Example: ["'Li Xunhuan' is a skilled martial artist.",
                                 "The 'Flying Dagger' is Li Xunhuan's signature weapon."]
        """
        print("InfoExtractor: Starting information extraction...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_extraction_prompt(text_to_analyze)

        # 2. Call the LLM service
        print("InfoExtractor: Sending request to LLM for extraction...")
        try:
            raw_response = self.llm_service.generate_text(task_prompt)
        except Exception as e:
            print(f"InfoExtractor: LLM call failed. Error: {e}")
            raise

        # 3. Parse the JSON response
        print("InfoExtractor: Parsing LLM response...")
        try:
            clean_response = raw_response.strip().replace("```json", "").replace("```", "").strip()
            # The expected response is a JSON object with a "facts" key
            extracted_data = json.loads(clean_response)
            facts = extracted_data.get("facts", [])
            if not isinstance(facts, list):
                raise ValueError("LLM response did not contain a valid list of facts.")

            print(f"InfoExtractor: Successfully extracted {len(facts)} facts.")
            return facts
        except (json.JSONDecodeError, ValueError) as e:
            print(f"InfoExtractor: Failed to parse JSON from LLM response. Error: {e}")
            print(f"Raw response was:\n{raw_response}")
            raise ValueError("Failed to decode LLM response into valid JSON.") from e

    def _build_extraction_prompt(self, text_to_analyze: str) -> str:
        """
        Builds the detailed prompt for the LLM to extract information.
        """
        prompt = f"""
You are an information extraction specialist. Your task is to read the following text and identify all key pieces of information that are important for maintaining story consistency.
Your output MUST be a single, valid JSON object and nothing else.

Extract facts about:
-   **Characters:** Names, descriptions, relationships, key actions, new abilities.
-   **Locations:** Names, descriptions, significance.
-   **Items:** Important objects, their properties, and who possesses them.
-   **Lore:** World-building rules, historical events, prophecies.

Each fact must be a concise, self-contained sentence.

--- TEXT TO ANALYZE ---
{text_to_analyze}
--- END OF TEXT ---

Based on your analysis, generate a JSON object with a single key "facts" which contains a list of these factual strings.

Example format:
{{
  "facts": [
    "Fact about a character.",
    "Fact about a location.",
    "A new relationship was formed between Character A and Character B."
  ]
}}

Remember, your entire response must be ONLY the JSON object.
"""
        # We use the base _construct_prompt to wrap this with persona info,
        # even though the default persona is neutral, this maintains consistency.
        return self._construct_prompt(prompt)
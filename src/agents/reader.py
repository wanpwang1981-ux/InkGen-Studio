# -*- coding: utf-8 -*-
"""
InkGen Studio - Reader Agent
============================

This module contains the Reader class, the agent responsible for quality
assurance and providing critical feedback.

It acts as a proxy for a human reader, evaluating a chapter's quality
against a set of criteria and deciding if it's ready or needs revision.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent
from typing import Dict, Any

class Reader(BaseAgent):
    """
    The agent responsible for reviewing and approving a refined chapter.

    This agent assesses the chapter based on plot consistency, character
    development, pacing, engagement, and adherence to the persona. It provides
    a final verdict: 'approved' or 'revision_needed'.
    """

    def run(self, refined_text: str, chapter_outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the review and approval process.

        Args:
            refined_text (str): The polished chapter text from the Refiner.
            chapter_outline (Dict[str, Any]): The original plan for the chapter,
                                              used for consistency checks.

        Returns:
            Dict[str, Any]: A dictionary containing the verdict.
                            Example: {'status': 'approved'} or
                            {'status': 'revision_needed', 'feedback': '...'}
        """
        import json

        print("Reader: Starting to review the refined chapter...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_review_prompt(refined_text, chapter_outline)

        # 2. Call the LLM service
        print("Reader: Sending request to LLM for chapter review...")
        try:
            raw_response = self.llm_service.generate_text(task_prompt)
        except Exception as e:
            print(f"Reader: LLM call failed during review. Error: {e}")
            raise

        # 3. Parse the JSON response from the LLM
        print("Reader: Parsing LLM review response...")
        try:
            clean_response = raw_response.strip().replace("```json", "").replace("```", "").strip()
            review_result = json.loads(clean_response)
            print(f"Reader: Successfully parsed review. Status: {review_result.get('status')}")
            return review_result
        except json.JSONDecodeError as e:
            print(f"Reader: Failed to parse JSON from LLM response. Error: {e}")
            print(f"Raw response was:\n{raw_response}")
            raise ValueError("Failed to decode LLM response into valid JSON.") from e

    def _build_review_prompt(self, refined_text: str, chapter_outline: Dict[str, Any]) -> str:
        """
        Builds the detailed prompt for the LLM to review a chapter.
        """
        prompt = f"""
You are a professional web novel reviewer and editor. Your task is to critically evaluate the following chapter based on its original outline and general quality standards.
Your output MUST be a single, valid JSON object and nothing else.

--- ORIGINAL CHAPTER OUTLINE ---
Title: {chapter_outline.get('title', 'N/A')}
Summary: {chapter_outline.get('summary', 'N/A')}
--- END OF OUTLINE ---

--- REFINED CHAPTER TEXT ---
{refined_text}
--- END OF TEXT ---

Please evaluate the chapter based on the following criteria:
1.  **Plot Adherence:** Does the chapter text faithfully follow the events described in the outline?
2.  **Quality of Writing:** Is the prose engaging, well-paced, and free of errors?
3.  **Persona Consistency:** Does the writing style match the agent's persona?
4.  **Engagement:** Is the chapter interesting? Does it make you want to read the next one?

Based on your evaluation, provide a verdict in the following JSON format:
{{
  "status": "approved | revision_needed",
  "feedback": "If revision is needed, provide a concise, actionable paragraph explaining what the Writer agent needs to change or add in the next attempt. Focus on concrete issues (e.g., 'The conflict with the villain felt rushed, add more dialogue to build tension'). If approved, this can be a short, positive comment."
}}

Choose 'approved' only if the chapter is excellent. Be critical.
Remember, your entire response must be ONLY the JSON object.
"""
        return self._construct_prompt(prompt)
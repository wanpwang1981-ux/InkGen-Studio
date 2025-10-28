# -*- coding: utf-8 -*-
"""
InkGen Studio - Refiner Agent
=============================

This module contains the Refiner class, the agent responsible for polishing
and improving the first draft of a chapter.

It focuses on language, style, and flow, rather than plot or structure.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent

class Refiner(BaseAgent):
    """
    The agent responsible for refining and polishing a chapter's draft.

    This agent takes the raw text from the Writer and improves its quality
    by correcting grammar, enhancing vocabulary, ensuring stylistic consistency
    with the persona, and improving the overall readability.
    """

    def run(self, draft_text: str) -> str:
        """
        Executes the text refining process.

        Args:
            draft_text (str): The first draft of the chapter text from the Writer.

        Returns:
            str: The refined and polished version of the chapter text.
        """
        print("Refiner: Starting to refine the draft...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_refining_prompt(draft_text)

        # 2. Call the LLM service
        print("Refiner: Sending request to LLM for text refinement...")
        try:
            refined_text = self.llm_service.generate_text(task_prompt)
            print("Refiner: Successfully refined the draft.")
            return refined_text
        except Exception as e:
            print(f"Refiner: LLM call failed during refinement. Error: {e}")
            raise

    def _build_refining_prompt(self, draft_text: str) -> str:
        """
        Builds the detailed prompt for the LLM to refine a chapter's text.
        """
        prompt = f"""
You are a master editor with a keen eye for style and flow. Your task is to refine and polish the following chapter draft.
You must adhere to the writing style defined by your current persona.
Do not change the core plot or events of the chapter. Your focus is on improving the quality of the writing itself.

Please perform the following actions:
- Correct any grammatical errors, spelling mistakes, or typos.
- Improve sentence structure and flow for better readability.
- Enhance the vocabulary and word choices to be more evocative and consistent with the persona.
- Ensure the tone and style are perfectly aligned with your persona's rules.

--- CHAPTER DRAFT TO REFINE ---
{draft_text}
--- END OF DRAFT ---

Now, provide the fully refined and polished version of the chapter.
"""
        return self._construct_prompt(prompt)
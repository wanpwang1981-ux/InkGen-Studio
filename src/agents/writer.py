# -*- coding: utf-8 -*-
"""
InkGen Studio - Writer Agent
============================

This module contains the Writer class, the agent responsible for generating
the first draft of a novel chapter.

It takes a detailed chapter outline and contextual information and turns it
into a full-length chapter text.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from .base_agent import BaseAgent
from typing import Dict, Any

class Writer(BaseAgent):
    """
    The agent responsible for writing the initial draft of a chapter.

    This agent's primary goal is content generation. It focuses on expanding
    an outline into a coherent and engaging narrative, adhering to the
    loaded persona.
    """

    def run(self, chapter_outline: Dict[str, Any], context: str, revision_feedback: str = None) -> str:
        """
        Executes the chapter writing process, either from scratch or based on feedback.

        Args:
            chapter_outline (Dict[str, Any]): The plan for this chapter.
            context (str): Context from previous chapters.
            revision_feedback (str, optional): Feedback from the Reader agent for revision.

        Returns:
            str: The generated or revised chapter text.
        """
        chapter_title = chapter_outline.get('title', 'Untitled Chapter')
        if revision_feedback:
            print(f"Writer: Starting to revise chapter '{chapter_title}' based on feedback...")
        else:
            print(f"Writer: Starting to write the first draft for chapter '{chapter_title}'...")

        # 1. Construct the detailed prompt for the LLM
        task_prompt = self._build_writing_prompt(chapter_outline, context, revision_feedback)

        # 2. Call the LLM service
        print(f"Writer: Sending request to LLM for chapter '{chapter_title}'...")
        try:
            generated_text = self.llm_service.generate_text(task_prompt)
            print(f"Writer: Successfully generated/revised draft for chapter '{chapter_title}'.")
            return generated_text
        except Exception as e:
            print(f"Writer: LLM call failed for chapter '{chapter_title}'. Error: {e}")
            raise

    def _build_writing_prompt(self, chapter_outline: Dict[str, Any], context: str, revision_feedback: str = None) -> str:
        """
        Builds the detailed prompt for the LLM to write or revise a chapter.
        """
        chapter_number = chapter_outline.get('chapter_number', 'N/A')
        title = chapter_outline.get('title', 'Untitled')
        summary = chapter_outline.get('summary', 'No summary provided.')

        if revision_feedback:
            # Prompt for revision
            prompt = f"""
You are a talented novelist. Your task is to revise a chapter based on the provided feedback.
You must adhere to your persona's writing style.

--- REVISION FEEDBACK ---
{revision_feedback}
--- END OF FEEDBACK ---

--- ORIGINAL CHAPTER OUTLINE ---
Chapter Number: {chapter_number}
Title: {title}
Summary of events: {summary}
--- END OF OUTLINE ---

Now, rewrite the entire chapter, incorporating the feedback to fix the issues.
The revised chapter should be a complete, high-quality piece of writing.
Begin the revised chapter now.
"""
        else:
            # Prompt for initial writing
            prompt = f"""
You are a talented novelist. Your current task is to write a full chapter for a web novel.
You must follow the instructions from your persona and the chapter outline provided below.
The chapter should be detailed, engaging, and at least 2000 words long.

--- CONTEXT FROM PREVIOUS CHAPTERS ---
{context if context else "This is the first chapter. No previous context."}
--- END OF CONTEXT ---

--- CURRENT CHAPTER OUTLINE ---
Chapter Number: {chapter_number}
Title: {title}
Summary of events to write: {summary}
--- END OF OUTLINE ---

Now, write the full chapter based on the outline and context. Ensure the writing style is consistent with your persona.
Begin the chapter now.
"""
        return self._construct_prompt(prompt)
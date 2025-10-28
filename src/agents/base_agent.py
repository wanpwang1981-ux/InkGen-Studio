# -*- coding: utf-8 -*-
"""
InkGen Studio - Base Agent Class
================================

This module defines the abstract base class for all AI agents in the system.
It provides a common structure and shared functionalities that all specialized
agents will inherit, such as handling personas, interacting with the LLM
service, and a standardized execution interface.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..llm_service import llm_service

class BaseAgent(ABC):
    """
    An abstract base class that defines the common interface for all AI agents.

    Each agent in the system is responsible for a specific task in the novel
    creation pipeline. This class ensures that they all share a consistent
    underlying structure.

    Attributes:
        persona (Dict[str, Any]): A dictionary containing the persona profile,
                                  which dictates the agent's style and behavior.
        llm_service: An instance of the LLMService for making API calls.
    """

    def __init__(self, persona: Dict[str, Any] = None):
        """
        Initializes the BaseAgent.

        Args:
            persona (Dict[str, Any], optional): The persona profile loaded from
                                                a JSON file. Defaults to a
                                                generic persona if None.
        """
        if persona is None:
            self.persona = self._get_default_persona()
        else:
            self.persona = persona

        # All agents will use the same singleton instance of the LLM service.
        self.llm_service = llm_service

    def _get_default_persona(self) -> Dict[str, Any]:
        """
        Provides a generic, default persona for when no specific one is loaded.
        """
        return {
            "name": "Generic Assistant",
            "version": "1.0",
            "description": "A helpful and neutral AI assistant.",
            "rules": {
                "narrative_style": {"pacing": "clear and concise"},
                "dialogue_style": {"length": "moderate"},
                "core_themes": ["clarity", "helpfulness"],
            }
        }

    def _construct_prompt(self, task_prompt: str) -> str:
        """
        Constructs the final prompt to be sent to the LLM.

        This method combines the agent's specific task instructions with the
        overarching rules defined in its loaded persona.

        Args:
            task_prompt (str): The specific instructions for the current task.

        Returns:
            str: A comprehensive, combined prompt ready for the LLM.
        """
        # Convert the persona rules into a readable string format.
        persona_rules = "\n".join([f"- {k}: {v}" for k, v in self.persona.get("rules", {}).items()])

        final_prompt = f"""
You are an AI assistant working on a novel.
Your current persona is '{self.persona.get('name', 'Unknown')}'.
Your persona description: {self.persona.get('description', 'N/A')}

You must adhere to the following persona rules:
{persona_rules}

Your current task is as follows:
---
{task_prompt}
---

Please provide your response based on these instructions.
"""
        return final_prompt.strip()

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        The main execution method for the agent.

        This method must be implemented by all subclasses. It defines the
        core logic of the agent's task. The signature can vary depending
        on the agent's needs.
        """
        pass
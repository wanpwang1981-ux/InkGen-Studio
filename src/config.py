# -*- coding: utf-8 -*-
"""
InkGen Studio - Configuration Loader
=====================================

This module handles the loading and parsing of application configuration
from environment variables stored in a .env file.

It ensures that necessary configurations, such as API keys, are available
to the rest of the application in a clean and accessible format.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root.
# This makes it easy to manage secrets without hardcoding them.
load_dotenv()

class Config:
    """
    A centralized class for application configuration.

    It reads environment variables, parses them, and provides them as
    class attributes. It also performs basic validation to ensure
    critical configurations are present.
    """
    def __init__(self):
        """
        Initializes the Config object by loading and parsing environment variables.
        """
        # Load the comma-separated API keys string from the environment.
        api_keys_str = os.getenv("GEMINI_API_KEYS")

        # Validate that the API keys variable is set.
        if not api_keys_str:
            raise ValueError(
                "GEMINI_API_KEYS environment variable not found or is empty. "
                "Please create a .env file based on .env.example and add your key(s)."
            )

        # Parse the string into a list of individual, stripped API keys.
        # This allows for flexible formatting in the .env file.
        self.api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]

        # Validate that the list of keys is not empty after parsing.
        if not self.api_keys:
            raise ValueError(
                "GEMINI_API_KEYS is defined but contains no valid keys after parsing. "
                "Please check the format in your .env file."
            )

        # Load the language model name, providing a default value if it's not set.
        self.model_name = os.getenv("LLM_MODEL_NAME", "gemini-pro")
        print(f"Configuration loaded. Using model: {self.model_name}")


# Create a single, globally accessible instance of the Config object.
# Other modules can simply `from src.config import config` to access settings.
config = Config()
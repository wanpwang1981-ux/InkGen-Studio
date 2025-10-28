# -*- coding: utf-8 -*-
"""
InkGen Studio - Knowledge Base Manager
======================================

This module provides a manager for handling the long-term memory of each
novel using a vector database (ChromaDB).

It abstracts the complexities of database interaction, providing a simple
interface for adding and querying knowledge specific to a novel.

Author: Jules
Date: 2025-09-30
Version: 1.0
"""

import chromadb
import uuid
from typing import List, Dict, Any

class KnowledgeBaseManager:
    """
    Manages the knowledge base for a single novel.

    Each novel gets its own 'collection' in ChromaDB to ensure that knowledge
    is not shared or leaked between different stories.
    """
    _client = None

    def __init__(self, novel_id: str):
        """
        Initializes the manager for a specific novel.

        Args:
            novel_id (str): A unique identifier for the novel, used as the
                            ChromaDB collection name.
        """
        if not KnowledgeBaseManager._client:
            # Initialize a persistent client that saves data to disk.
            KnowledgeBaseManager._client = chromadb.PersistentClient(path="kb_storage")

        # Get or create a collection for this specific novel.
        self.collection = KnowledgeBaseManager._client.get_or_create_collection(name=novel_id)
        self.novel_id = novel_id
        print(f"KnowledgeBaseManager initialized for novel '{novel_id}'.")

    def add(self, documents: List[str]):
        """
        Adds new pieces of knowledge to the novel's knowledge base.

        Each document is a string containing a single piece of information.
        (e.g., "Character 'John Doe' is a detective from New York.")

        Args:
            documents (List[str]): A list of strings to add to the KB.
        """
        if not documents:
            return

        print(f"Adding {len(documents)} new knowledge entries to '{self.novel_id}' KB.")
        # Generate unique IDs for each document
        ids = [str(uuid.uuid4()) for _ in documents]

        self.collection.add(
            documents=documents,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Queries the knowledge base to find relevant information.

        Args:
            query_text (str): The question or topic to search for.
            n_results (int): The maximum number of results to return.

        Returns:
            List[str]: A list of the most relevant knowledge documents.
        """
        if not query_text:
            return []

        print(f"Querying '{self.novel_id}' KB for: '{query_text}'...")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        # The result is a list containing one list of documents, so we extract it.
        return results.get('documents', [[]])[0]

    def get_all_knowledge(self) -> List[str]:
        """
        Retrieves all documents currently in the collection.
        Useful for providing a full context dump.
        """
        print(f"Retrieving all knowledge from '{self.novel_id}' KB.")
        all_items = self.collection.get()
        return all_items.get('documents', [])
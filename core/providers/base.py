"""
Base module for LLM providers.

This module defines the base class for all LLM providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, Any]:  # noqa: E501
        """
        Execute a chat against the provider, with history

        Args:
            messages: List of messages to send to the provider
            config: Configuration dictionary with provider-specific settings

        Returns:
            Dictionary containing the response and metadata
        """
        pass

    @abstractmethod
    async def execute_prompt(self, system_prompt: str, user_prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:  # noqa: E501
        """
        Execute a prompt against the provider

        Args:
            system_prompt: The system prompt to use
            user_prompt: The user prompt to test
            config: Configuration dictionary with provider-specific settings

        Returns:
            Dictionary containing the response and metadata
        """
        pass

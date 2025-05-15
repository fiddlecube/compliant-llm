"""
Base module for result evaluators.

This module defines the base class for all evaluators that assess LLM responses.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseEvaluator(ABC):
    """Base class for result evaluators"""
    
    @abstractmethod
    async def evaluate(self, 
                system_prompt: str,
                user_prompt: str, 
                llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an LLM response
        
        Args:
            system_prompt: The system prompt used in the test
            user_prompt: The user prompt used in the test
            llm_response: The response from the LLM provider
            
        Returns:
            Dictionary containing evaluation results
        """
        pass

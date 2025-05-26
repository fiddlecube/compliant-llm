"""
Base module for result evaluators.

This module defines the base class for all evaluators that assess LLM responses.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseEvaluator(ABC):
    """Base class for result evaluators"""
    
    @abstractmethod
    async def evaluate(self, system_prompt: str, user_prompt: str, llm_response: Dict[str, Any]) -> Dict[str, Any]:
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


class BaseAttackEvaluator(BaseEvaluator):
    """Base class for attack strategy evaluators"""
    
    async def _extract_response_text(self, llm_response: Dict[str, Any]) -> str:
        """
        Extract text content from an LLM response in various formats
        
        Args:
            llm_response: The response from the LLM provider
            
        Returns:
            Extracted text content
        """
        response_text = ''
        
        # Extract text from LiteLLM response format
        if isinstance(llm_response, dict):
            # Handle standard response format
            if 'response' in llm_response and 'choices' in llm_response['response']:
                choices = llm_response['response']['choices']
                if choices and 'message' in choices[0]:
                    response_text = choices[0]['message'].get('content', '')
            # Alternative format
            elif 'choices' in llm_response:
                choices = llm_response['choices']
                if choices and 'message' in choices[0]:
                    response_text = choices[0]['message'].get('content', '')
            # Direct content field
            elif 'content' in llm_response:
                response_text = llm_response['content']
            # Handle key response in response
            elif 'response' in llm_response:
                response_text = llm_response['response']
                
        # If we couldn't extract text through known formats, try as string
        if not response_text and isinstance(llm_response, str):
            response_text = llm_response
        return response_text


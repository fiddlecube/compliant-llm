"""
LiteLLM provider implementation.

This module implements a provider that uses LiteLLM to interact with various LLM APIs.
"""
from typing import Dict, Any
import asyncio
from .base import LLMProvider


class LiteLLMProvider(LLMProvider):
    """Provider that uses LiteLLM to interact with LLM APIs"""
    
    async def execute_prompt(self, 
                      system_prompt: str, 
                      user_prompt: str, 
                      config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a prompt using LiteLLM
        
        Args:
            system_prompt: The system prompt to use
            user_prompt: The user prompt to test
            config: Configuration with provider-specific settings
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Import litellm here to avoid dependency issues
            from litellm import acompletion
            
            # Extract provider-specific configuration
            # TODO: @vini - simplify this
            model = config.get("model", "gpt-3.5-turbo")
            temperature = config.get("temperature", 0.7)
            timeout = config.get("timeout", 30)
            api_key = config.get("api_key")
            
            # Execute the prompt
            response = await acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                timeout=timeout,
                api_key=api_key
            )
            
            return {
                "success": True,
                "response": response,
                "provider": "litellm",
                "model": model
            }
            
        except Exception as e:
            # Handle errors
            return {
                "success": False,
                "error": str(e),
                "provider": "litellm",
                "model": config.get("model", "gpt-3.5-turbo")
            }

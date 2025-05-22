"""
LiteLLM provider implementation.

This module implements a provider that uses LiteLLM to interact with various LLM APIs.
"""
from typing import Dict, Any, List
import logging
import re
from .base import LLMProvider


logger = logging.getLogger(__name__)


def clean_json_response(response: str) -> str:
    """
    Clean the JSON response from the LLM by removing markdown code blocks.

    Args:
        response: The response string from the LLM

    Returns:
        Cleaned JSON string
    """
    if response is None:
        return response

    # Handle markdown code blocks with JSON content
    # First try to extract content between ```json and ``` markers
    json_block_match = re.search(
        r"```json\s*([\s\S]*?)\s*```", response, re.DOTALL
    )
    if json_block_match:
        return json_block_match.group(1)

    # Then try to extract content between generic ``` and ``` markers
    code_block_match = re.search(
        r"```\s*([\s\S]*?)\s*```", response, re.DOTALL
    )
    if code_block_match:
        return code_block_match.group(1)

    # If no code blocks found but response starts with ```json or ends with ```
    response = re.sub(r"^```json\s*", "", response)
    response = re.sub(r"\s*```$", "", response)

    # Ensure the JSON string is properly formatted
    # response = response.strip()
    # if not response.startswith("{"):
    #     response = "{" + response
    # if not response.endswith("}"):
    #     response += "}"

    return response


class LiteLLMProvider(LLMProvider):
    """Provider that uses LiteLLM to interact with LLM APIs"""
    def __init__(self):
        self.history = []

    async def chat(self, messages: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, Any]:  # noqa: E501
        try:
            # Import litellm here to avoid dependency issues
            from litellm import acompletion  # Using acompletion instead of completion for async
            chat_history = self.history + messages
            # Extract provider-specific configuration
            provider_config = config.get("provider_config", {})
            model = provider_config.get("provider_name", "gpt-4o")
            temperature = provider_config.get("temperature", 0.7)
            timeout = provider_config.get("timeout", 30)
            api_key = provider_config.get("api_key")
            # Execute the prompt asynchronously
            response = await acompletion(
                model=model,
                messages=chat_history,
                temperature=temperature,
                timeout=timeout,
                api_key=api_key
            )

            # Properly extract the message and add to history in the correct format
            if response and hasattr(response, 'choices') and response.choices:
                message_to_add = {
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }
                self.history.append(message_to_add)

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "provider": "litellm",
                "model": model
            }

        except Exception as e:
            # Handle errors
            return {
                "success": False,
                "error": str(e),
                "provider": "litellm",
                "model": provider_config.get("model", "openai/gpt-4o")
            }

    async def execute_prompt(self, system_prompt: str, user_prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:  # noqa: E501
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
            
            # Extract the message content in the same way as the chat method
            if response and hasattr(response, 'choices') and response.choices:
                response_content = response.choices[0].message.content
            else:
                response_content = "No response generated"

            return {
                "success": True,
                "response": response_content,  # Return just the content, not the whole object
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

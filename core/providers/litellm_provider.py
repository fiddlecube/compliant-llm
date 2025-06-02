"""
LiteLLM provider implementation.

This module implements a provider that uses LiteLLM to interact with various LLM APIs.
"""
from typing import Dict, Any, List
import logging
import re
import yaml
import json
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

    return response

def clean_yaml_response(response: str) -> str:
    """
    Clean the YAML response from the LLM by removing markdown code blocks.

    Args:
        response: The response string from the LLM

    Returns:
        Cleaned YAML string
    """
    # Handle markdown code blocks with YAML content
    # First try to extract content between ```yaml and ``` markers
    yaml_block_match = re.search(
        r"```yaml\s*([\s\S]*?)\s*```", response, re.DOTALL
    )
    if yaml_block_match:
        return yaml_block_match.group(1).strip()

    # Then try to extract content between generic ``` and ``` markers
    code_block_match = re.search(
        r"```\s*([\s\S]*?)\s*```", response, re.DOTALL
    )
    if code_block_match:
        return code_block_match.group(1).strip()

    # If no code blocks found but response starts with ```yaml or ends with ```
    response = re.sub(r"^```yaml\s*", "", response)
    response = re.sub(r"\s*```$", "", response)

    return response.strip()

def clean_response(response: str) -> str:
    """
    Clean the response from the LLM by removing markdown code blocks.
    Attempts to determine if the response is JSON or YAML and applies
    the appropriate cleaning function.

    Args:
        response: The response string from the LLM

    Returns:
        Cleaned response string
    """
    # Remove any leading/trailing whitespace
    cleaned_response = response.strip()
    
    try:
        
        # First check if the response is in a code block
        code_block_match = re.search(
            r"(?:```[ \t]*(yaml|json)?[ \t]*\n?)?([\s\S]+?)(?:```|\Z)", 
            cleaned_response, 
            re.IGNORECASE
        )
        if code_block_match:
            # Extract language tag and content
            language_tag = code_block_match.group(1)
            if language_tag is None:
                language_tag = ''
            content = code_block_match.group(2).strip()
            
            # If content is empty, return the original response
            if not content:
                return cleaned_response
            
            # If we have an explicit language tag, validate content format
            if language_tag == 'yaml':
                try:
                    # Validate YAML syntax without modifying content
                    yaml.safe_load(content)
                    return content
                except Exception:
                    # If YAML parsing fails, return the original content without changes
                    return content
            elif language_tag == 'json':
                try:
                    # Validate JSON syntax without modifying content
                    json.loads(content)
                    return content
                except Exception:
                    # If JSON parsing fails, return the original content without changes
                    return content
            else:
                # No explicit language tag, return the extracted content
                return content
        
        # If no code block found, return the original response
        return cleaned_response
    except Exception as e:
        print("Error cleaning response", cleaned_response, e)
        return cleaned_response


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
            timeout = provider_config.get("timeout", 180)
            # Execute the prompt asynchronously
            response = await acompletion(
                model=model,
                messages=chat_history,
                temperature=temperature,
                timeout=timeout,
                num_retries=provider_config.get("num_retries", 3),
                cooldown_time=provider_config.get("cooldown_time", 60),
            )

            # Properly extract the message and add to history in the correct format
            if response and hasattr(response, 'choices') and response.choices:
                message_to_add = {
                    "role": "assistant",
                    "content": clean_response(response.choices[0].message.content)
                }
                self.history.append(message_to_add)

            return {
                "success": True,
                "response": response.choices[0].message.content or "",
                "tool_calls": response.choices[0].message.tool_calls,
                "provider": "litellm",
                "model": model
            }

        except Exception as e:
            # Handle errors
            logger.error(f"Error executing prompt: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "litellm",
                "model": provider_config.get("model", None)
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
            provider_config = config.get("provider_config", {})
            model = provider_config.get("provider_name")
            temperature = provider_config.get("temperature", 0.7)
            timeout = provider_config.get("timeout", 30)
            # Execute the prompt
            response = await acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                timeout=timeout,
                num_retries=provider_config.get("num_retries", 3),
                cooldown_time=provider_config.get("cooldown_time", 60),
                turn_off_message_logging=True,
            )
            
            # Extract the message content in the same way as the chat method
            if response and hasattr(response, 'choices') and response.choices:
                response_content = response.choices[0].message.content
                response_content = clean_response(response_content)
            else:
                response_content = "No response generated"

            return {
                "success": True,
                "response": response_content,  # Return just the content, not the whole object
                "tool_calls": response.choices[0].message.tool_calls,
                "provider": "litellm",
                "model": model
            }

        except Exception as e:
            # Handle errors
            return {
                "success": False,
                "error": str(e),
                "provider": "litellm",
                "model": config.get("model")
            }

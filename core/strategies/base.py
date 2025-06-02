"""
Base module for attack strategies.

This module defines the base class for all attack strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.providers.base import LLMProvider
from datetime import datetime
import aiohttp
import asyncio
import json


import logging
logger = logging.getLogger(__name__)

class BaseAttackStrategy(ABC):
    """Base class for all attack strategies"""
    
    @abstractmethod
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
        """
        Generate attack prompts based on configuration
        
        Args:
            config: Configuration dictionary for the strategy
            
        Returns:
            List of dictionaries containing attack data with at least a 'prompt' key
        """
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the strategy"""
        pass
           
    def run(self, system_prompt: str, provider, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run the strategy synchronously"""
        import asyncio
        return asyncio.run(self.a_run(system_prompt, provider, config))
    
    @abstractmethod
    async def a_run(self, system_prompt: str, provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run the strategy asynchronously against a system prompt.
        
        Args:
            system_prompt: The system prompt to test
            provider: LLM provider instance to use for executing prompts
            config: Additional configuration for the strategy
            
        Returns:
            List of result dictionaries containing prompts, responses, and evaluations
        """
        results = []
        attack_prompts = await self.get_attack_prompts(config, system_prompt)
        
        for attack_data in attack_prompts:
            user_prompt = attack_data['prompt']
            try:
                # Execute against provider
                response = await provider.execute_prompt(
                    system_prompt,
                    user_prompt,
                    config or {}
                )
                
                # Evaluate the response
                evaluation = await self.evaluate(system_prompt, user_prompt, response)
                
                # Compile result
                result = {
                    'strategy': self.name,
                    'user_prompt': user_prompt,
                    'response': response,
                    'evaluation': evaluation,
                    'success': evaluation.get('passed', False)
                }
                results.append(result)
            except Exception as e:
                # Handle errors
                results.append({
                    'strategy': self.name,
                    'user_prompt': user_prompt,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    @abstractmethod
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the response to determine if the attack was successful.
        Default implementation considers all attacks as successful (needs to be overridden).
        
        Args:
            system_prompt: The system prompt that was tested
            user_prompt: The user prompt that was used for the attack
            response: The response from the provider
            
        Returns:
            Dictionary containing evaluation results with at least a 'passed' key
        """
        pass

    async def _run_blackbox_test(
        self,
        attack_instruction: str,
        api_config: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a single blackbox test against an API.

        This method handles the common blackbox testing logic and is called from
        within a_run_blackbox_test.
        
        Args:
            attack_data: Attack data containing prompt and metadata
            api_config: API configuration including URL, headers, etc.
            config: Optional configuration for the test
            
        Returns:
            Dict containing test results
            
        Raises:
            ValueError: If required fields are missing from the payload
            Exception: If API request fails
        """
        try:
            # Validate API configuration
            if not api_config.get('url'):
                raise ValueError("API URL is required")
            
            # Prepare the API request
            url = api_config['url']
            headers = api_config.get('headers', {})

            # Make API request with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            url,
                            headers=headers,
                            json=api_config['payload']
                        ) as response:
                            if response.status != 200:
                                error_msg = f"API request failed with status {response.status}"
                                if attempt == max_retries - 1:
                                    raise Exception(error_msg)
                                await asyncio.sleep(1)  # Exponential backoff
                                continue
                            
                            api_response = await response.json()
                            break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(1)  # Exponential backoff
                    continue

        except Exception as e:
            print(f"[red]API Test Failed: {str(e)}[/red]")
            api_response = {'error': str(e)}

        # Evaluate the response
        evaluation = await self.evaluate(
            "",  # Empty for blackbox testing
            attack_instruction,
            api_response,
            config or {}
        )

        # Prepare result
        result = {
            'strategy': self.name,
            'system_prompt': "",
            'attack_prompt': attack_instruction,
            'instruction': attack_instruction,
            'category': "blackbox",
            'response': api_response,
            'evaluation': evaluation,
            'success': evaluation.get('passed', False),
            'mutation_technique': "",
            'is_blackbox': True
        }

        return result

    async def a_run_blackbox_test(self, attack_instruction: str, api_config: Dict[str, Any], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run blackbox testing against an API.
        
        This is a template method that orchestrates blackbox testing.
        
        Args:
            api_config: API configuration including URL, headers, etc.
            config: Configuration parameters
            
        Returns:
            List of blackbox test results
        """
        results = []
        start_time = datetime.now()

        # # Run each test
        # for attack_data in attack_prompts:
        result = await self._run_blackbox_test(attack_instruction, api_config, config)
        results.append(result)

        return {
            "strategy": self.name,
            "results": results,
            "runtime_in_seconds": (datetime.now() - start_time).total_seconds(),
            "is_blackbox": True
        }

"""
Base module for attack strategies.

This module defines the base class for all attack strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.providers.base import LLMProvider
from datetime import datetime
import aiohttp


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
    
    async def _run_blackbox_test(self, attack_data: Dict[str, Any], api_config: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a single blackbox test against an API.

        Called from within a_run_blackbox_test
        
        This is a template method that handles the common blackbox testing logic.
        
        Args:
            attack_data: Attack data containing prompt and metadata
            api_config: API configuration including URL, headers, etc.
            
        Returns:
            Dict containing test results
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_config['url'],
                    json={"messages": [{"role": "user", "content": attack_data.get('attack_instruction', '')}]},
                    headers=api_config.get('headers', {})
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}")
                    api_response = await response.json()
        except Exception as e:
            api_response = {'error': str(e)}

        evaluation = await self.evaluate(
            "",  # Empty for blackbox testing
            attack_data.get('attack_instruction', ''),
            api_response,
            config
        )

        return {
            'strategy': self.name,
            'system_prompt': "",
            'attack_prompt': attack_data.get('attack_instruction', ''),
            'instruction': attack_data.get('instruction', ''),
            'category': attack_data.get('category', ''),
            'response': api_response,
            'evaluation': evaluation,
            'success': evaluation.get('passed', False),
            'mutation_technique': attack_data.get('mutation_technique', ''),
            'is_blackbox': True
        }

    async def a_run_blackbox_test(self, attack_data: Any, api_config: Dict[str, Any], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
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
        result = await self._run_blackbox_test(attack_data, api_config, config)
        results.append(result)

        return {
            "strategy": self.name,
            "results": results,
            "runtime_in_seconds": (datetime.now() - start_time).total_seconds(),
            "is_blackbox": True
        }
    
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

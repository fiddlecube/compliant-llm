"""
Advanced Context Manipulation attack strategies.

This module implements specialized context manipulation techniques to test LLM security:
- Long-form context poisoning
- Temporal manipulation
- Contextual overloading
- Multi-turn manipulation
- Embedded instruction hijacking
"""

from typing import Dict, List, Any
import asyncio
import os
import re
import yaml
import random

from ...base import BaseAttackStrategy
from core.providers.base import LLMProvider
from core.evaluators.evals.attack_evaluator import ContextManipulationEvaluator


class AdvancedContextManipulationStrategy(BaseAttackStrategy):
    """
    Advanced strategy that attempts to manipulate the context window of the LLM.
    
    This strategy leverages techniques beyond basic context manipulation:
    - Long-form context poisoning: Overwhelm with details to hide manipulative content
    - Temporal manipulation: Create confusion about past/future instructions
    - Contextual overloading: Provide excessive context to obscure manipulation
    - Multi-turn manipulation: Set up manipulations across multiple interactions
    - Embedded instruction hijacking: Hide instructions within seemingly benign content
    """
    
    # Class-level cache for attack data
    _cached_attack_data = {}
    
    def _load_instructions(self) -> List[Dict[str, Any]]:
        """
        Load attack prompts from the data.yaml file
        
        Returns:
            List of technique entries from the data file
        """
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(current_dir, 'data.yaml')
        
        try:
            with open(data_file, 'r') as f:
                data = yaml.safe_load(f)
                
            if 'techniques' in data:
                return data['techniques']
            else:
                return []
        except Exception as e:
            print(f"Error loading context manipulation data: {e}")
            return []
    
    async def get_attack_prompts(self, config: Dict[str, Any], 
                              system_prompt: str) -> List[Dict[str, Any]]:
        """
        Generate advanced context manipulation attack prompts
        
        Args:
            config: Configuration dictionary for the strategy
            system_prompt: The system prompt to be tested
            
        Returns:
            List of dictionaries containing attack data with prompts and metadata
        """
        # Get configuration options
        max_prompts = config.get("max_prompts_per_strategy", 10)
        
        # Check if we already have cached attack data for this system prompt
        # Create a deterministic cache key based on the system prompt and sample size
        cache_key = f"{hash(system_prompt)}_{max_prompts}"
        
        if cache_key in AdvancedContextManipulationStrategy._cached_attack_data:
            return AdvancedContextManipulationStrategy._cached_attack_data[cache_key]
        
        # Load techniques from data.yaml
        techniques = self._load_instructions()
        
        # Sample up to max_prompts techniques
        sample_size = min(max_prompts, len(techniques))
        sampled_techniques = random.sample(techniques, sample_size)
        
        attack_data = []
        for technique in sampled_techniques:
            # Get technique information
            technique_id = technique.get('id', '')
            technique_name = technique.get('name', '')
            
            # Get prompts for this technique
            prompts = technique.get('prompts', [])
            if prompts:
                # Choose a random prompt from the available ones
                prompt = random.choice(prompts)
                
                # Check if this technique requires multi-turn interaction
                is_multi_turn = technique.get('is_multi_turn', False)
                
                # Add to attack data
                attack_data.append({
                    'prompt': prompt,
                    'category': 'context_manipulation',
                    'technique': technique_id,
                    'technique_name': technique_name,
                    'is_multi_turn': is_multi_turn
                })
        
        # Cache the generated attack data
        AdvancedContextManipulationStrategy._cached_attack_data[cache_key] = attack_data
        return attack_data
    
    async def process_attack_prompt(self, config: Dict[str, Any], 
                                    attack_data: Dict[str, Any],
                                    provider: LLMProvider, 
                                    system_prompt: str) -> Dict[str, Any]:
        """
        Process a single attack prompt asynchronously
        
        Args:
            config: Configuration dictionary
            attack_data: Dictionary with attack prompt and metadata
            provider: LLM provider instance
            system_prompt: The system prompt to test
            
        Returns:
            Dictionary with results for this specific attack prompt
        """
        user_prompt = attack_data.get('prompt', '')
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Execute against provider
            response = await provider.chat(messages, config or {})
            
            # Evaluate the response
            evaluation = await self.evaluate(system_prompt, user_prompt, response)
            
            # Compile result with detailed metadata
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'response': response,
                'evaluation': evaluation,
                'success': evaluation.get('passed', False),
                'technique': attack_data.get('technique', 'advanced_context_manipulation'),
                'technique_name': attack_data.get('technique_name', ''),
                'is_multi_turn': attack_data.get('is_multi_turn', False),
                'category': attack_data.get('category', 'context_manipulation')
            }
        except Exception as e:
            # Handle errors
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'error': str(e),
                'success': False,
                'technique': attack_data.get('technique', 'advanced_context_manipulation'),
                'technique_name': attack_data.get('technique_name', ''),
                'is_multi_turn': attack_data.get('is_multi_turn', False),
                'category': attack_data.get('category', 'context_manipulation')
            }
            
    async def a_run(self, system_prompt: str, provider: LLMProvider, 
                   config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Run the advanced context manipulation strategy asynchronously with parallel execution
        
        Args:
            system_prompt: The system prompt to test
            provider: LLM provider instance to use for executing prompts
            config: Additional configuration for the strategy
            
        Returns:
            List of result dictionaries containing prompts, responses, and evaluations
        """
        # Get attack prompts
        attack_prompts = await self.get_attack_prompts(config or {}, system_prompt)
        
        # Process all attack prompts in parallel
        tasks = [
            self.process_attack_prompt(config or {}, attack_data, provider, system_prompt)
            for attack_data in attack_prompts
        ]
        results = await asyncio.gather(*tasks)
        return results
    
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if the advanced context manipulation was successful
        
        Args:
            system_prompt: The system prompt that was tested
            user_prompt: The user prompt that was used for the attack
            response: The response from the provider
            
        Returns:
            Dictionary containing evaluation results with at least a 'passed' key
        """
        evaluator = ContextManipulationEvaluator()
        return await evaluator.evaluate(system_prompt, user_prompt, response)
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return "AdvancedContextManipulationStrategy"

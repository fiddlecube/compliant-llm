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
       
        
        try:
            data_file_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
            with open(data_file_path, 'r') as file:
                content = file.read()
                entries = yaml.safe_load(content)
                AdvancedContextManipulationStrategy._cached_instruction_entries = entries
                return entries
        except Exception as e:
            print(f"Error loading context manipulation data: {e}")
            return []
    
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
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
        
        attack_prompts = []
        for entry in sampled_techniques:
            # Get a random mutation from available options
            if "mutations" in entry and entry["mutations"]:
                mutation = random.choice(entry["mutations"])
                attack_prompts.append({
                    "attack_instruction": mutation["obfuscated_prompt"],
                    "system_prompt": system_prompt,
                    "category": self.name,
                    "severity": entry.get("severity", "medium"),
                    "mutation_technique": mutation.get("technique", ""),
                    "description": entry.get("description", ""),
                    "target_behavior": entry.get("target_behavior", "")
                })
        
        # Cache the generated attack data
        AdvancedContextManipulationStrategy._cached_attack_data[cache_key] =  attack_prompts
        return attack_prompts
    
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
        attack_prompt = attack_data.get('attack_instruction', attack_data.get('attack_prompt', ''))
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": attack_prompt}
        ]
        
        try:
            # Execute against provider
            response = await provider.chat(messages, config or {})
            
            # Evaluate the response
            evaluation = await self.evaluate(system_prompt, attack_prompt, response)
            
            # Add target behavior to evaluation if available
            target_behavior = attack_data.get('target_behavior', '')
            if target_behavior and 'target_behavior' not in evaluation:
                evaluation['target_behavior'] = target_behavior
                
            # Compile result with detailed metadata
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'attack_prompt': attack_prompt,
                'target_behavior': attack_data.get('target_behavior', ''),
                'response': response,
                'evaluation': evaluation,
                'success': evaluation.get('passed', False),
                'mutation_technique': attack_data.get('mutation_technique', ''),
                'is_multi_turn': attack_data.get('is_multi_turn', False),
                'category': attack_data.get('category', 'context_manipulation')
            }
        except Exception as e:
            # Handle errors
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'attack_prompt': attack_prompt,
                'error': str(e),
                'success': False,
                'mutation_technique': attack_data.get('mutation_technique', ''),
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
        return "context_manipulation"

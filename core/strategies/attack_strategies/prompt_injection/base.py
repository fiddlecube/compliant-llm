
# flake8: noqa E501
"""
Prompt injection strategy for red teaming LLM systems.

This module implements a strategy for testing prompt security by attempting to inject
malicious instructions into the system prompt, evaluating the LLM's response to determine
if it successfully bypassed safeguards.
"""
from typing import Dict, List, Any
import random
import os
import re
import uuid
import yaml
from ...base import BaseAttackStrategy
from core.providers.base import LLMProvider
from core.evaluators.evals.attack_evaluator import PromptInjectionEvaluator

class PromptInjectionStrategy(BaseAttackStrategy):
    """
    Strategy that attempts to inject malicious instructions into the prompt.
    
    This strategy uses techniques to override or manipulate the system prompt,
    attempting to make the LLM follow new instructions.
    """
    
    # Class variables to cache loaded instruction entries and generated attack data
    _cached_instruction_entries: Any = None
    _cached_attack_data: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return "prompt_injection"
    
    def _load_instructions(self):
        """Load malicious instructions from YAML file"""
        if PromptInjectionStrategy._cached_instruction_entries is not None:
            instruction_entries = PromptInjectionStrategy._cached_instruction_entries
        else:
            # Path to the data.yaml file (relative to this module)
            data_file_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
            
            # Load malicious instructions from YAML
            try:
                with open(data_file_path, 'r') as file:
                    data = yaml.safe_load(file)
                    instruction_entries = data
                    
                    # Filter out any entries marked as benign
                    instruction_entries = [entry for entry in instruction_entries 
                                          if isinstance(entry, dict) and not entry.get('benign', False)]
                    
                    # Cache the filtered entries for future use
                    PromptInjectionStrategy._cached_instruction_entries = instruction_entries

            except Exception as e:
                # Fallback to default list if there's an error loading the file
                print(f"Error loading data.yaml: {e}")
                instruction_entries = []
        return instruction_entries
    
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
        """Generate prompt injection attack prompts"""

        # Use cached instruction entries if available
        instruction_entries = self._load_instructions()
        
        # Sample prompts (or fewer if there aren't enough)
        sample_size = min(10, len(instruction_entries))
        sampled_entries = random.sample(instruction_entries, sample_size) if instruction_entries else []
        
        # Check if we already have cached attack data for this system prompt
        # Create a deterministic cache key based on the system prompt and sample size to ensure uniqueness
        cache_key = f"{hash(system_prompt)}_{sample_size}"
        
        if cache_key in PromptInjectionStrategy._cached_attack_data:
            return PromptInjectionStrategy._cached_attack_data[cache_key]
            
        # Generate attack data
        attack_data = []
        
        # Generate attack prompts by combining instructions with templates
        for entry in sampled_entries:
            # Select a mutation at random if available, otherwise use original_prompt
            if 'mutations' in entry and entry['mutations']:
                # Get the mutation object (which has technique and obfuscated_prompt)
                mutation = random.choice(entry['mutations'])
                mutation_technique = mutation['technique']
                instruction_template = mutation['obfuscated_prompt']
            else:
                # Fallback to original prompt if no mutations
                mutation_technique = None
                instruction_template = entry['original_prompt']
            
            # Replace any case variant of __PROMPT__ with system_prompt
            # Using regex to match __PROMPT__ case-insensitively
            instruction = re.sub(r'__PROMPT__', system_prompt, instruction_template, flags=re.IGNORECASE)
            
            attack_data.append({
                'system_prompt': system_prompt,
                'category': self.name,
                'attack_instruction': instruction,
                'mutation_technique': mutation_technique
            })
        
        # Cache the generated attack data
        PromptInjectionStrategy._cached_attack_data[cache_key] = attack_data
                
        return attack_data
    
    async def process_attack_prompt(self, config: Dict[str, Any], attack_data: Dict[str, Any], provider: LLMProvider, system_prompt: str):
        """Process a single attack prompt asynchronously"""
        attack_prompt = attack_data.get('attack_instruction', attack_data.get('attack_prompt', ''))
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": attack_prompt}
        ]
        try:
            # Execute against provider
            response = await provider.chat(messages, config)
            # clean up response here, remove unwanted elements
            
            # Evaluate the response
            evaluation = await self.evaluate(system_prompt, attack_prompt, response, config)
            
            # Compile result
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'attack_prompt': attack_prompt,
                'category': attack_data.get('category', ''),
                'mutation_technique': attack_data.get('mutation_technique', ''),
                'response': response,
                'evaluation': evaluation,
                'success': evaluation.get('passed', False)
            }
        except Exception as e:
                # Handle errors
                return {
                    'strategy': self.name,
                    'system_prompt': system_prompt,
                    'attack_prompt': attack_prompt,
                    'mutation_technique': attack_data.get('mutation_technique', ''),
                    'error': str(e),
                    'success': False
                }
        
    async def attack_and_evaluate(self, system_prompt: str, attack_prompts: List[Dict[str, Any]], provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the prompt injection strategy asynchronously with parallel execution"""
        import asyncio
        
        
        # Process all attack prompts in parallel
        tasks = [self.process_attack_prompt(config, attack_data, provider, system_prompt) for attack_data in attack_prompts]
        results = await asyncio.gather(*tasks)
        return results
        
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if the prompt injection was successful"""
        evaluator = PromptInjectionEvaluator()
        llm_evaluate = await evaluator.llm_evaluate(system_prompt, user_prompt, response, config)
        return llm_evaluate
    
    async def a_run(self, system_prompt: str, provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the prompt injection strategy asynchronously"""
        results = []
        attack_prompts = await self.get_attack_prompts(config, system_prompt)
        results = await self.attack_and_evaluate(system_prompt, attack_prompts, provider, config)
        return results
        
    
       
    
   

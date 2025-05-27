# flake8: noqa E501
"""
Jailbreak strategy for red teaming LLM systems.

This module implements a strategy for testing prompt security by attempting to bypass
LLM safeguards through jailbreak techniques.
"""
from typing import Dict, List, Any
import random
import asyncio
import datetime
import os
import re
import yaml
from ...base import BaseAttackStrategy
from core.providers.base import LLMProvider
from core.evaluators.evals.attack_evaluator import JailbreakEvaluator

class JailbreakStrategy(BaseAttackStrategy):
    """
    Strategy that uses various jailbreak techniques to bypass LLM safeguards.
    
    This strategy contains a collection of prompts designed to trick the LLM into
    ignoring its safety guidelines and providing harmful or restricted content.
    """
    
    # Class variables to cache loaded instruction entries and generated attack data
    _cached_instruction_entries: Any = None
    _cached_attack_data: Dict[str, Any] = {}
    
    def __init__(self):
        self._load_data()
    
    def _load_data(self):
        """Load jailbreak data from YAML file"""
        data_file_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
        try:
            with open(data_file_path, 'r') as file:
                content = file.read()
                self._data = yaml.safe_load(content)
        except Exception as e:
            print(f"Error loading data.yaml: {e}")
            self._data = []
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return "jailbreak"
    
    def _load_instructions(self):
        """Load malicious instructions from YAML file"""
        if JailbreakStrategy._cached_instruction_entries is not None:
            instruction_entries = JailbreakStrategy._cached_instruction_entries
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
                    JailbreakStrategy._cached_instruction_entries = instruction_entries

            except Exception as e:
                # Fallback to default list if there's an error loading the file
                print(f"Error loading data.yaml: {e}")
                instruction_entries = []
        return instruction_entries
    
    
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
        """Generate jailbreak attack prompts"""
        # Get configuration options
        max_prompts = config.get("max_prompts_per_strategy", 10)
        
        attack_data = []
        
        # Get all entries from data.yaml
        entries = self._load_instructions()
        
        # Sample up to max_prompts entries
        sample_size = min(max_prompts, len(entries))
        sampled_entries = random.sample(entries, sample_size)
        
        # Check if we already have cached attack data for this system prompt
        # Create a deterministic cache key based on the system prompt and sample size to ensure uniqueness
        cache_key = f"{hash(system_prompt)}_{sample_size}"
        
        if cache_key in JailbreakStrategy._cached_attack_data:
            return JailbreakStrategy._cached_attack_data[cache_key]
        
        for entry in sampled_entries:
            original_prompt = entry['original_prompt']
            
            if 'mutations' in entry and entry['mutations']:
                # Get the mutation object (which has technique and obfuscated_prompt)
                mutation = random.choice(entry['mutations'])
                mutation_technique = mutation['technique']
                instruction_template = mutation['obfuscated_prompt']
            else:
                # Fallback to original prompt if no mutations
                mutation_technique = None
                instruction_template = entry['original_prompt']
             
            # replace original_prompt with query   
            instruction = re.sub(r'{query}', original_prompt, instruction_template, flags=re.IGNORECASE)
            
            attack_data.append({
                'system_prompt': system_prompt,
                'category': self.name,
                'attack_instruction': instruction,
                'mutation_technique': mutation_technique
            })
        
        # Cache the generated attack data
        JailbreakStrategy._cached_attack_data[cache_key] = attack_data
        return attack_data
    
    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load all entries from data.yaml"""
        entries = []
        if not self._data:
            print("No data loaded")
            return []
        
        if isinstance(self._data, dict):
            for entry in self._data.get('entries', []):
                if isinstance(entry, dict) and 'original_prompt' in entry and 'mutations' in entry:
                    entries.append(entry)
        elif isinstance(self._data, list):
            for entry in self._data:
                if isinstance(entry, dict) and 'original_prompt' in entry and 'mutations' in entry:
                    entries.append(entry)
        else:
            print(f"Unexpected data type: {type(self._data)}")
        
        return entries
    
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
            
            # Evaluate the response
            evaluation = await self.evaluate(system_prompt, attack_prompt, response, config)
            
            # Compile result
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'attack_prompt': attack_prompt,
                'instruction': attack_data.get('instruction', ''),
                'category': attack_data.get('category', ''),
                'response': response,
                'evaluation': evaluation,
                'success': evaluation.get('passed', False),
                'mutation_technique': attack_data.get('mutation_technique', ''),
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
            }
    
    async def a_run(self, system_prompt: str, provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the jailbreak strategy asynchronously with parallel execution"""
        
       # Get attack prompts
        attack_prompts = await self.get_attack_prompts(config, system_prompt)
       
        
        # Process all attack prompts in parallel
        tasks = [self.process_attack_prompt(config, attack_data, provider, system_prompt) for attack_data in attack_prompts]
        results = await asyncio.gather(*tasks)
        return results
    
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if the jailbreak was successful"""
        evaluator = JailbreakEvaluator()
        llm_evaluate = await evaluator.llm_evaluate(system_prompt, user_prompt, response, config)
        return llm_evaluate

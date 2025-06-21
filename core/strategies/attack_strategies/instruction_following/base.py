"""
Instruction Following strategy for red teaming LLM systems.

This module implements a strategy for testing instruction following capabilities by evaluating
if the model correctly follows user instructions, especially multi-step or edge-case commands.
"""
from typing import Dict, List, Any
import random
import os
import yaml
from ...base import BaseAttackStrategy
from core.providers.base import LLMProvider
from core.evaluators.evals.attack_evaluator import InstructionFollowingEvaluator

class InstructionFollowingStrategy(BaseAttackStrategy):
    """
    Strategy that evaluates if the model correctly follows user instructions.
    
    This strategy tests the model's ability to follow complex, multi-step instructions
    and handle edge cases in instruction following.
    """
    
    # Class variables to cache loaded instruction entries and generated attack data
    _cached_instruction_entries: Any = None
    _cached_attack_data: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return "instruction_following"
    
    def _load_instructions(self):
        """Load instruction following test cases from YAML file"""
        if InstructionFollowingStrategy._cached_instruction_entries is not None:
            instruction_entries = InstructionFollowingStrategy._cached_instruction_entries
        else:
            # Path to the data.yaml file (relative to this module)
            data_file_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
            
            # Load instruction following test cases from YAML
            try:
                with open(data_file_path, 'r') as file:
                    data = yaml.safe_load(file)
                    instruction_entries = data
                    
                    # Cache the entries for future use
                    InstructionFollowingStrategy._cached_instruction_entries = instruction_entries

            except Exception as e:
                # Fallback to default list if there's an error loading the file
                print(f"Error loading data.yaml: {e}")
                instruction_entries = []
        return instruction_entries
    
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
        """Generate instruction following test prompts"""

        # Use cached instruction entries if available
        instruction_entries = self._load_instructions()
        
        # Sample prompts (or fewer if there aren't enough)
        sample_size = min(10, len(instruction_entries))
        sampled_entries = random.sample(instruction_entries, sample_size) if instruction_entries else []
        
        # Check if we already have cached attack data for this system prompt
        # Create a deterministic cache key based on the system prompt and sample size to ensure uniqueness
        cache_key = f"{hash(system_prompt)}_{sample_size}"
        
        if cache_key in InstructionFollowingStrategy._cached_attack_data:
            return InstructionFollowingStrategy._cached_attack_data[cache_key]
            
        # Generate attack data
        attack_data = []
        
        # Generate test prompts from the instruction entries
        for entry in sampled_entries:
            instruction = entry.get('instruction', '')
            expected_behavior = entry.get('expected_behavior', '')
            category = entry.get('category', 'general')
            difficulty = entry.get('difficulty', 'medium')
            
            attack_data.append({
                'system_prompt': system_prompt,
                'category': self.name,
                'attack_instruction': instruction,
                'expected_behavior': expected_behavior,
                'test_category': category,
                'difficulty': difficulty
            })
        
        # Cache the generated attack data
        InstructionFollowingStrategy._cached_attack_data[cache_key] = attack_data
                
        return attack_data
    
    async def process_attack_prompt(self, config: Dict[str, Any], attack_data: Dict[str, Any], provider: LLMProvider, system_prompt: str):
        """Process a single instruction following test prompt asynchronously"""
        attack_prompt = attack_data.get('attack_instruction', '')
        expected_behavior = attack_data.get('expected_behavior', '')
        test_category = attack_data.get('test_category', 'general')
        difficulty = attack_data.get('difficulty', 'medium')
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": attack_prompt}
        ]
        try:
            # Execute against provider
            response = await provider.chat(messages, config)
            
            # Evaluate the response
            evaluation = await self.evaluate(system_prompt, attack_prompt, response, config, expected_behavior)
            
            # Compile result
            return {
                'strategy': self.name,
                'system_prompt': system_prompt,
                'attack_prompt': attack_prompt,
                'category': attack_data.get('category', ''),
                'test_category': test_category,
                'difficulty': difficulty,
                'expected_behavior': expected_behavior,
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
                    'test_category': test_category,
                    'difficulty': difficulty,
                    'expected_behavior': expected_behavior,
                    'error': str(e),
                    'success': False
                }
        
    async def attack_and_evaluate(self, system_prompt: str, attack_prompts: List[Dict[str, Any]], provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the instruction following strategy asynchronously with parallel execution"""
        import asyncio
        
        # Process all attack prompts in parallel
        tasks = [self.process_attack_prompt(config, attack_data, provider, system_prompt) for attack_data in attack_prompts]
        results = await asyncio.gather(*tasks)
        return results
        
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any], config: Dict[str, Any] = None, expected_behavior: str = None) -> Dict[str, Any]:
        """Evaluate if the instruction following was successful"""
        evaluator = InstructionFollowingEvaluator()
        llm_evaluate = await evaluator.llm_evaluate(system_prompt, user_prompt, response, config, expected_behavior)
        return llm_evaluate
    
    async def a_run(self, system_prompt: str, provider: LLMProvider, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run the instruction following strategy asynchronously"""
        results = []
        attack_prompts = await self.get_attack_prompts(config, system_prompt)
        results = await self.attack_and_evaluate(system_prompt, attack_prompts, provider, config)
        return results 
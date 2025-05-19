# flake8: noqa E501
"""
Jailbreak strategy for red teaming LLM systems.

This module implements a strategy for testing prompt security by attempting to bypass
LLM safeguards through jailbreak techniques.
"""
from typing import Dict, List, Any
import random
import os
import yaml
from ...base import BaseAttackStrategy
from core.providers.base import LLMProvider

class JailbreakStrategy(BaseAttackStrategy):
    """
    Strategy that uses various jailbreak techniques to bypass LLM safeguards.
    
    This strategy contains a collection of prompts designed to trick the LLM into
    ignoring its safety guidelines and providing harmful or restricted content.
    """
    
    def __init__(self):
        self._load_data()
    
    def _load_data(self):
        """Load jailbreak data from YAML file"""
        data_file_path = os.path.join(os.path.dirname(__file__), 'data.yaml')
        try:
            with open(data_file_path, 'r') as file:
                data = yaml.safe_load(file)
                self._base_queries = data.get('base_queries', [])
                self._jailbreak_templates = data.get('jailbreak_templates', [])
                self._compliance_indicators = data.get('evaluation_indicators', {}).get('compliance', [])
                self._refusal_indicators = data.get('evaluation_indicators', {}).get('refusal', [])
        except Exception as e:
            print(f"Error loading data.yaml: {e}")
            self._base_queries = []
            self._jailbreak_templates = []
            self._compliance_indicators = []
            self._refusal_indicators = []
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return "JailbreakStrategy"
    
    async def get_attack_prompts(self, config: Dict[str, Any], system_prompt: str) -> List[Dict[str, Any]]:
        """Generate jailbreak attack prompts"""
        # Get configuration options
        max_prompts = config.get("max_prompts_per_strategy", 10)
        use_all_templates = config.get("use_all_jailbreak_templates", False)
        
        attack_data = []
        
        # Generate attack prompts by combining queries with templates
        for query in self._base_queries[:max_prompts]:
            if use_all_templates:
                # Use all templates with this query
                for template in self._jailbreak_templates:
                    jailbreak_prompt = template.format(
                        query=query,
                        system_prompt=system_prompt
                    )
                    
                    attack_data.append({
                        'prompt': jailbreak_prompt,
                        'category': 'jailbreak',
                        'attack_instruction': query,
                        'system_prompt': system_prompt
                    })
            else:
                # Use a random template for this query
                template = random.choice(self._jailbreak_templates)
                jailbreak_prompt = template.format(
                    query=query,
                    system_prompt=system_prompt
                )
                
                attack_data.append({
                    'prompt': jailbreak_prompt,
                    'category': 'jailbreak',
                    'attack_instruction': query, # the instruction that was used to generate the attack prompt
                    'system_prompt': system_prompt
                })
                
        return attack_data
    
    async def a_run(self, system_prompt: str, provider: LLMProvider, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run the jailbreak strategy asynchronously"""
        results = []
        attack_prompts = await self.get_attack_prompts(config or {}, system_prompt)
        
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
                    'attack_instruction': attack_data.get('attack_instruction', ''),
                    'category': attack_data.get('category', ''),
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
                    'attack_instruction': attack_data.get('attack_instruction', ''),
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if the jailbreak was successful"""
        return {}

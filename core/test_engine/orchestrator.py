# flake8: noqa E501
"""
Attack orchestrator module.

This module orchestrates attack strategies against LLM providers.
"""
from typing import Dict, List, Any
from datetime import datetime
from ..strategies.base import BaseAttackStrategy
from ..providers.base import LLMProvider
from ..evaluators.base import BaseEvaluator


class AttackOrchestrator:
    """Orchestrates attack strategies against LLM providers"""
    
    def __init__(self, 
                 strategies: List[BaseAttackStrategy], 
                 provider: LLMProvider, 
                 evaluator: BaseEvaluator, 
                 config: Dict[str, Any]):
        """
        Initialize the orchestrator
        
        Args:
            strategies: List of attack strategies
            provider: LLM provider
            evaluator: Response evaluator
            config: Configuration dictionary
        """
        self.strategies = strategies
        self.provider = provider
        self.evaluator = evaluator
        self.config = config
    
    async def collect_attack_prompts(self, system_prompt: str) -> List[Dict[str, Any]]:
        """
        Collect all attack prompts from registered strategies
        
        Returns:
            List of dictionaries with prompt and strategy information
        """
        all_prompts = []
        for strategy in self.strategies:
            # Get prompts from each strategy
            prompts = await strategy.get_attack_prompts(self.config, system_prompt)
            
            # Check if this is an enhanced strategy that has enhancement metadata
            has_enhancement_info = hasattr(strategy, 'get_enhancement_info')
            
            # Add strategy information to each prompt
            for prompt in prompts:
                prompt_data = {
                    "prompt": prompt, 
                    "strategy": strategy.name
                }
                
                # TODO: Add enhancement info if available
                        
                all_prompts.append(prompt_data)
                
        return all_prompts
    
    async def execute_single_attack(self, system_prompt: str, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single attack and evaluate results
        
        Args:
            system_prompt: The system prompt to test
            attack_data: Dictionary with attack prompt and strategy
            
        Returns:
            Dictionary with test results and evaluation
        """
        user_prompt = attack_data["prompt"]["attack_instruction"]
        strategy = attack_data["prompt"]["category"]
        
        # Execute against provider
        response = await self.provider.execute_prompt(
            system_prompt, 
            user_prompt, 
            self.config
        )
        
        # Evaluate the response
        evaluation = await self.evaluator.evaluate(
            system_prompt,
            user_prompt,
            response
        )
        
        # Compile result
        result = {
            "user_prompt": user_prompt,
            "strategy": strategy,
            "response": response,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add enhancement info if available
        enhancement_info = attack_data.get("enhancement", None)
        if enhancement_info:
            result["enhancement"] = enhancement_info
        
        return result

    async def orchestrate_attack(self, system_prompt: str, strategies: List[BaseAttackStrategy]) -> List[Dict[str, Any]]:
        """Run the orchestrator"""
        attack_prompts = await self.collect_attack_prompts(system_prompt)
        results = []
        for strategy in strategies:
            strategy_results = await strategy.a_run(system_prompt, self.provider, self.config)
            results.extend(strategy_results)
        print("====strategy_results====", len(results))
        return results
        
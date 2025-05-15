"""
Attack orchestrator module.

This module orchestrates attack strategies against LLM providers.
"""
from typing import Dict, List, Any
import asyncio
from datetime import datetime
from .strategies.base import BaseAttackStrategy
from .providers.base import LLMProvider
from .evaluators.base import BaseEvaluator


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
    
    async def collect_attack_prompts(self) -> List[Dict[str, Any]]:
        """
        Collect all attack prompts from registered strategies
        
        Returns:
            List of dictionaries with prompt and strategy information
        """
        all_prompts = []
        for strategy in self.strategies:
            # Get prompts from each strategy
            prompts = await strategy.get_attack_prompts(self.config)
            # Add strategy information to each prompt
            all_prompts.extend([{
                "prompt": prompt, 
                "strategy": strategy.name
            } for prompt in prompts])
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
        user_prompt = attack_data["prompt"]
        strategy = attack_data["strategy"]
        
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
        return {
            "user_prompt": user_prompt,
            "strategy": strategy,
            "response": response,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        }

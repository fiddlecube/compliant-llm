# flake8: noqa E501
"""
Attack orchestrator module.

This module orchestrates attack strategies against LLM providers.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..strategies.base import BaseAttackStrategy
from ..providers.base import LLMProvider
from ..evaluators.base import BaseEvaluator


class AttackOrchestrator:
    """Orchestrates attack strategies against LLM providers"""
    
    def __init__(self, 
                 strategies: List[BaseAttackStrategy], 
                 provider: LLMProvider, 
                 config: Dict[str, Any],
                 evaluator: BaseEvaluator | None = None):
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
    
    async def orchestrate_attack(self, system_prompt: str, strategies: List[BaseAttackStrategy]) -> List[Dict[str, Any]]:
        """Run the orchestrator"""
        results = []
        for strategy in strategies:
            strategy_results = await strategy.a_run(system_prompt, self.provider, self.config)
            results.extend(strategy_results)
        return results

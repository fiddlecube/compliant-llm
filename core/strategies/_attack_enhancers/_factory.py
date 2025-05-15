"""Factory for creating enhanced attack strategies.

This module provides factory functions for creating enhanced attack strategies
that combine existing strategies with attack enhancers.
"""
from typing import List, Dict, Any

from core.strategies.base import BaseAttackStrategy
from core.strategies.attack_enhancers.basic_attacks.base import (
    AttackEnhancement,
)
from core.strategies.attack_enhancers.enhanced_strategy import (
    EnhancedAttackStrategy,
)


class EnhancedStrategyFactory:
    """Factory for creating enhanced attack strategies"""

    @staticmethod
    async def create_enhanced_strategy(
        base_strategy: BaseAttackStrategy,
        enhancers: List[AttackEnhancement],
        config: Dict[str, Any],
    ) -> BaseAttackStrategy:
        """Create an enhanced attack strategy by combining a base strategy with enhancers

        Args:
            base_strategy: The original attack strategy
            enhancers: List of enhancers to apply
            config: Configuration dictionary

        Returns:
            An enhanced attack strategy
        """
        # Get the base prompts from the original strategy
        base_prompts = await base_strategy.get_attack_prompts(config)

        # Create the enhanced strategy
        strategy_name = f"Enhanced_{base_strategy.name}"
        return EnhancedAttackStrategy(base_prompts, enhancers, strategy_name)

    @staticmethod
    async def create_all_enhanced_strategies(
        base_strategies: List[BaseAttackStrategy],
        enhancers: List[AttackEnhancement],
        config: Dict[str, Any],
    ) -> List[BaseAttackStrategy]:
        """Create enhanced strategies for multiple base strategies

        Args:
            base_strategies: List of original attack strategies
            enhancers: List of enhancers to apply
            config: Configuration dictionary

        Returns:
            List of enhanced attack strategies
        """
        enhanced_strategies = []

        for strategy in base_strategies:
            enhanced = await EnhancedStrategyFactory.create_enhanced_strategy(
                strategy, enhancers, config
            )
            enhanced_strategies.append(enhanced)

        return enhanced_strategies

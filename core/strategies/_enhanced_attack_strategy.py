"""Enhanced attack strategy module that combines strategy and enhancement capabilities.

This module provides a unified approach to attack strategies with built-in
enhancement capabilities.
"""
from typing import List, Dict, Any, Optional, Callable
from abc import abstractmethod

from .base import BaseAttackStrategy
from .attack_enhancers.basic_attacks.base import AttackEnhancement

# TODO: [@Vini] this can be simplified.
class EnhancedAttackStrategy(BaseAttackStrategy):
    """Enhanced attack strategy that combines strategy and enhancement capabilities.
    
    This class simplifies the architecture by:
    1. Implementing BaseAttackStrategy interface
    2. Having built-in enhancement capabilities
    3. Providing factory methods for creating enhanced strategies
    4. Eliminating the need for separate adapter and factory classes
    """

    def __init__(
        self,
        strategy_name: str,
        enhancers: Optional[List[AttackEnhancement]] = None,
        base_prompts: Optional[List[str]] = None,
        prompt_generator: Optional[Callable[[Dict[str, Any]], List[str]]] = None,
    ):
        """Initialize the enhanced attack strategy
        
        Args:
            strategy_name: Name of this strategy
            enhancers: List of enhancers to apply (optional)
            base_prompts: List of base attack prompts to enhance (optional)
            prompt_generator: Function that generates prompts based on config (optional)
            
        At least one of base_prompts or prompt_generator must be provided.
        """
        self._name = strategy_name
        self.enhancers = enhancers or []
        self.base_prompts = base_prompts or []
        self.prompt_generator = prompt_generator
        self._enhancement_metadata: Dict[str, Dict[str, Any]] = {}
        
        if not self.base_prompts and not self.prompt_generator:
            raise ValueError(
                "Either base_prompts or prompt_generator must be provided"
            )

    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return self._name

    async def get_attack_prompts(self, config: Dict[str, Any]) -> List[str]:
        """Generate attack prompts, potentially enhancing them
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of attack prompts (enhanced if enhancers are present)
        """
        self._enhancement_metadata = {}
        
        # Get base prompts either from the provided list or generator function
        base_prompts = self.base_prompts
        if self.prompt_generator:
            generated_prompts = self.prompt_generator(config)
            base_prompts = base_prompts + generated_prompts
            
        # If no enhancers, just return the base prompts
        if not self.enhancers:
            return base_prompts
            
        # Apply enhancers to base prompts
        return await self._enhance_prompts(base_prompts, config)
    
    async def _enhance_prompts(
        self, prompts: List[str], config: Dict[str, Any]
    ) -> List[str]:
        """Apply enhancers to the base prompts
        
        Args:
            prompts: List of base prompts to enhance
            config: Configuration dictionary
            
        Returns:
            List of enhanced prompts
        """
        enhanced_prompts = []
        
        for prompt in prompts:
            # Add the original prompt if specified in config
            include_original = config.get("include_original_prompts", True)
            if include_original:
                enhanced_prompts.append(prompt)
                self._enhancement_metadata[prompt] = {
                    "enhanced": False,
                    "original_prompt": prompt,
                }
            
            # Apply each enhancer to the prompt
            for enhancer in self.enhancers:
                result = await enhancer.a_enhance(prompt)
                enhanced_prompt = result.output_text
                enhanced_prompts.append(enhanced_prompt)
                
                # Store metadata about this enhancement for later retrieval
                self._enhancement_metadata[enhanced_prompt] = {
                    "enhanced": True,
                    "enhancer": enhancer.name,
                    "original_prompt": prompt,
                    "metadata": result.metadata
                }
        
        return enhanced_prompts
    
    def get_enhancement_info(self, prompt: str) -> Dict[str, Any]:
        """Get enhancement information for a specific prompt
        
        Args:
            prompt: The enhanced prompt to get info for
            
        Returns:
            Dictionary with enhancement information or empty dict if not enhanced
        """
        return self._enhancement_metadata.get(prompt, {})
        
    @classmethod
    async def create_from_strategy(
        cls,
        base_strategy: BaseAttackStrategy,
        enhancers: List[AttackEnhancement],
        config: Dict[str, Any],
    ) -> "EnhancedAttackStrategy":
        """Create an enhanced strategy from an existing strategy
        
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
        return cls(
            strategy_name=strategy_name,
            enhancers=enhancers,
            base_prompts=base_prompts
        )
    
    @classmethod
    async def create_from_prompts(
        cls,
        strategy_name: str,
        prompts: List[str],
        enhancers: List[AttackEnhancement]
    ) -> "EnhancedAttackStrategy":
        """Create an enhanced strategy from a list of prompts
        
        Args:
            strategy_name: Name for the strategy
            prompts: List of prompts to enhance
            enhancers: List of enhancers to apply
            
        Returns:
            An enhanced attack strategy
        """
        return cls(
            strategy_name=strategy_name,
            enhancers=enhancers,
            base_prompts=prompts
        )
    
    @classmethod
    async def enhance_all_strategies(
        cls,
        strategies: List[BaseAttackStrategy],
        enhancers: List[AttackEnhancement],
        config: Dict[str, Any],
    ) -> List["EnhancedAttackStrategy"]:
        """Create enhanced strategies for multiple base strategies
        
        Args:
            strategies: List of original attack strategies
            enhancers: List of enhancers to apply
            config: Configuration dictionary
            
        Returns:
            List of enhanced attack strategies
        """
        enhanced_strategies = []
        
        for strategy in strategies:
            enhanced = await cls.create_from_strategy(
                strategy, enhancers, config
            )
            enhanced_strategies.append(enhanced)
        
        return enhanced_strategies

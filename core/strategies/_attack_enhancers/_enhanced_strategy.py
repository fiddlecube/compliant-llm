"""Enhanced attack strategy that applies various attack enhancers to base prompts.

This module provides an adapter for using attack enhancers with the orchestrator.
"""
from typing import List, Dict, Any

from core.strategies.base import BaseAttackStrategy
from core.strategies._attack_enhancers.basic_attacks.base import AttackEnhancement   # noqa: E501


class EnhancedAttackStrategy(BaseAttackStrategy):
    """A strategy that enhances base attack prompts using various enhancers.
    This adapter makes attack enhancers compatible with the orchestrator flow.
    """

    def __init__(
        self,
        base_prompts: List[str],
        enhancers: List[AttackEnhancement],
        strategy_name: str = "EnhancedAttackStrategy",
    ):
        """Initialize the enhanced attack strategy

        Args:
            base_prompts: List of base attack prompts to enhance
            enhancers: List of enhancers to apply to each prompt
            strategy_name: Name of this strategy
        """
        self.base_prompts = base_prompts
        self.enhancers = enhancers
        self._name = strategy_name
        self._enhancement_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def get_attack_prompts(self, config: Dict[str, Any]) -> List[str]:
        """Generate enhanced attack prompts by applying enhancers to base prompts

        Args:
            config: Configuration dictionary

        Returns:
            List of enhanced attack prompts
        """
        enhanced_prompts = []
        self._enhancement_metadata = {}

        for prompt in self.base_prompts:
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
    
    @property
    def name(self) -> str:
        """Return the name of the strategy"""
        return self._name

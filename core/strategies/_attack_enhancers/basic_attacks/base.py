#  attack enhancements taken from deepeval
from abc import ABC, abstractmethod
from typing import Dict

from core.models.prompt_converter import (
    PromptDataType as AttackEnhancementDataType,
)
from core.strategies.attack_enhancers.base import AttackEnhancementResult


class AttackEnhancement(ABC):
    @abstractmethod
    def enhance(self, attack: str, *args, **kwargs) -> AttackEnhancementResult:
        """Enhance the given attack synchronously."""
        pass

    async def a_enhance(
        self, attack: str, *args, **kwargs
    ) -> AttackEnhancementResult:
        """Enhance the given attack asynchronously."""
        return self.enhance(
            attack, *args, **kwargs
        )  # Default to sync behavior
    
    async def convert_async(
        self, *, prompt: str, input_type: AttackEnhancementDataType = "text"
    ) -> AttackEnhancementResult:
        """
        Converts the given prompts into a different representation

        Args:
            prompt: The prompt to be converted.
            input_type: The type of the input.

        Returns:
            AttackEnhancementResult: The result of the conversion.
        """
        # By default, we just use the enhance method
        return await self.a_enhance(prompt)
    
    def input_supported(self, input_type: AttackEnhancementDataType) -> bool:
        """
        Checks if the input type is supported by the converter

        Args:
            input_type: The input type to check

        Returns:
            bool: True if the input type is supported, False otherwise
        """
        # By default, we only support text
        return input_type == "text"
    
    def output_supported(self, output_type: AttackEnhancementDataType) -> bool:
        """
        Checks if the output type is supported by the converter

        Args:
            output_type: The output type to check

        Returns:
            bool: True if the output type is supported, False otherwise
        """
        # By default, we only support text
        return output_type == "text"
    
    @property
    def name(self) -> str:
        """Return the name of the enhancement"""
        return self.__class__.__name__

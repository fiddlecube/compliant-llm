#  attack enhancements taken from deepeval
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict

from core.models.prompt_converter import (
    PromptDataType as AttackEnhancementDataType,
)


@dataclass
class AttackEnhancementResult:
    output_text: str
    output_type: AttackEnhancementDataType
    metadata: Dict = field(default_factory=dict)


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

    @abstractmethod
    async def convert_async(
        self, *, prompt: str, input_type: AttackEnhancementDataType = "text"
    ) -> AttackEnhancementResult:
        """
        Converts the given prompts into a different representation

        Args:
            prompt: The prompt to be converted.

        Returns:
            str: The converted representation of the prompts.
        """

    @abstractmethod
    def input_supported(self, input_type: AttackEnhancementDataType) -> bool:
        """
        Checks if the input type is supported by the converter

        Args:
            input_type: The input type to check

        Returns:
            bool: True if the input type is supported, False otherwise
        """

    @abstractmethod
    def output_supported(self, output_type: AttackEnhancementDataType) -> bool:
        """
        Checks if the output type is supported by the converter

        Args:
            output_type: The output type to check

        Returns:
            bool: True if the output type is supported, False otherwise
        """

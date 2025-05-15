import random

from core.strategies._attack_enhancers.base import AttackEnhancementResult
from core.strategies._attack_enhancers.basic_attacks.base import AttackEnhancement  # noqa: E501

from .template import PromptInjectionTemplate


class PromptInjection(AttackEnhancement):
    def enhance(self, attack: str) -> AttackEnhancementResult:
        """Enhance the attack input using prompt injection techniques."""
        output_text = random.choice(
            [
                PromptInjectionTemplate.enhance_1(attack),
                PromptInjectionTemplate.enhance_2(attack),
            ]
        )
        return AttackEnhancementResult(
            output_text=output_text,
            output_type="text",
            metadata={"attack_enhancement": "prompt_injection"},
        )

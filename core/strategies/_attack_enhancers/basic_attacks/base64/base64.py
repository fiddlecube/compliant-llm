import base64

from core.strategies._attack_enhancers.base import AttackEnhancementResult
from core.strategies._attack_enhancers.basic_attacks.base import AttackEnhancement  # noqa: E501


class Base64(AttackEnhancement):
    def enhance(self, attack: str) -> AttackEnhancementResult:
        """Enhance the attack using Base64 encoding."""
        output_text = base64.b64encode(attack.encode()).decode()
        return AttackEnhancementResult(
            output_text=output_text,
            output_type="text",
            metadata={"attack_enhancement": "base64"},
        )

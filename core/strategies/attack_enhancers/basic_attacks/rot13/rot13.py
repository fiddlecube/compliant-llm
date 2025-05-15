from core.strategies.attack_enhancers.base import AttackEnhancementResult
from core.strategies.attack_enhancers.basic_attacks.base import AttackEnhancement  # noqa: E501


class Rot13(AttackEnhancement):
    def enhance(self, attack: str) -> AttackEnhancementResult:
        """Enhance the attack using ROT13 encoding."""
        output_text = attack.translate(
            str.maketrans(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
            )
        )
        return AttackEnhancementResult(
            output_text=output_text,
            output_type="text",
            metadata={"attack_enhancement": "rot13"},
        )

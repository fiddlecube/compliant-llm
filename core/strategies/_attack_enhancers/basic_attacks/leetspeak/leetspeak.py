from core.strategies._attack_enhancers.base import AttackEnhancementResult
from core.strategies._attack_enhancers.basic_attacks.base import AttackEnhancement  # noqa: E501


class Leetspeak(AttackEnhancement):
    def enhance(self, attack: str) -> AttackEnhancementResult:
        """Enhance the attack using Leetspeak transformation."""
        leet_map = {
            "a": "4",
            "e": "3",
            "i": "1",
            "o": "0",
            "s": "5",
            "t": "7",
            "l": "1",
            "A": "4",
            "E": "3",
            "I": "1",
            "O": "0",
            "S": "5",
            "T": "7",
            "L": "1",
        }
        output_text = "".join(leet_map.get(char, char) for char in attack)
        return AttackEnhancementResult(
            output_text=output_text,
            output_type="text",
            metadata={"attack_enhancement": "leetspeak"},
        )

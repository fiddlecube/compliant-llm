from enum import Enum


class AttackEnhancement(Enum):
    NONE = "None"
    GRAY_BOX_ATTACK = "Gray Box Attack"
    PROMPT_INJECTION = "Prompt Injection"
    # PROMPT_PROBING = "Prompt Probing"
    # JAILBREAK_CRESCENDO = "Crescendo Jailbreak"
    # JAILBREAK_LINEAR = "Linear Jailbreak"
    JAILBREAK_TREE = "Tree Jailbreak"
    ROT13 = "ROT13 Encoding"
    BASE64 = "Base64 Encoding"
    LEETSPEAK = "Leetspeak Encoding"
    # MATH_PROBLEM = "Math Problem"
    # MULTILINGUAL = "Multilingual"
    IMAGE = "Image"
    QR_CODE = "QR Code"

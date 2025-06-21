# flake8: noqa E501
"""
Constants for OWASP Top 10 for LLMs and Attack Strategies

This module defines the mappings between OWASP Top 10 for LLMs vulnerabilities
and the corresponding attack strategies implemented in the project.
It also catalogs the mutation techniques available for each strategy.
"""

from enum import Enum
from typing import Dict, List, Any

# OWASP Top 10 for LLMs mapping to attack strategies
# Based on: https://owasp.org/www-project-top-10-for-large-language-model-applications/
ATTACK_STRATEGIES = {
    # Prompt Injection strategies
    "prompt_injection": {
        "owasp_category": ["LLM01"],
        "owasp_name": "Prompt Injection",
        "description": "Manipulating an LLM by crafting inputs that exploit the model's training and prompt handling to override instructions or manipulate outputs."
    },
    
    # Data Poisoning strategies
    "data_poisoning": {
        "owasp_category": ["LLM05"],
        "owasp_name": "Supply Chain Vulnerabilities",
        "description": "Testing for vulnerabilities related to poisoned training data, compromised model weights, or backdoors through trigger phrases and malicious associations."
    },
    "indirect_prompt_injection": {
        "owasp_category": ["LLM01"],
        "owasp_name": "Prompt Injection",
        "description": "Manipulating an LLM by crafting inputs that exploit the model's training and prompt handling to override instructions or manipulate outputs."
    },
    
    # Insecure Output Handling strategies
    "insecure_output_handling": {
        "owasp_category": ["LLM02", "LLM07"],
        "owasp_name": ["Insecure Output Handling", "Insecure Plugin Design"],
        "description": "Failure to properly validate and sanitize LLM outputs before using them in sensitive operations or displaying to users."
    },
    
    # Sensitive Information Disclosure/Training Data Poisoning strategies
    "sensitive_info_disclosure": {
        "owasp_category": ["LLM03", "LLM06"],
        "owasp_name": ["Training Data Poisoning", "Sensitive Information Disclosure"],
        "description": "Unauthorized exposure of confidential data, personal information, or system details through LLM interactions."
    },

    # Model Denial of Service strategies
    "model_dos": {
        "owasp_category": ["LLM04"],
        "owasp_name": "Model Denial of Service",
        "description": "Disrupting LLM availability by exploiting resource constraints or deliberate overloading tactics."
    },
    
    # Excessive Agency strategies
    "excessive_agency": {
        "owasp_category": ["LLM08"],
        "owasp_name": "Excessive Agency",
        "description": "LLM systems that can take actions beyond their intended scope or authority, potentially causing harm."
    },
    
    # Model Theft/Extraction strategies
    "model_extraction": {
        "owasp_category": ["LLM10"],
        "owasp_name": "Model Theft",
        "description": "Unauthorized extraction of model weights, architecture, or training data through inference attacks or other techniques."
    },
    
    # Jailbreak (General strategy, maps to multiple OWASP categories)
    "jailbreak": {
        "owasp_category": ["LLM01", "LLM02", "LLM08"],
        "owasp_name": ["Prompt Injection", "Insecure Output Handling", "Excessive Agency"],
        "description": "Attempts to bypass LLM security measures and constraints to generate prohibited content."
    }
}

# Cross-reference dictionary for looking up strategies by OWASP category
OWASP_CATEGORY_TO_STRATEGIES = {
    "LLM01": ["prompt_injection", "indirect_prompt_injection", "jailbreak"],
    "LLM02": ["insecure_output_handling", "jailbreak"],
    "LLM03": ["sensitive_info_disclosure"],
    "LLM04": ["model_dos"],
    "LLM05": ["data_poisoning"],
    "LLM06": ["sensitive_info_disclosure"],
    "LLM07": ["insecure_output_handling"],
    "LLM08": ["excessive_agency", "jailbreak"],
    "LLM09": ["excessive_agency"],
    "LLM10": ["model_extraction"]
}

# Attack strategy mutation techniques
ATTACK_STRATEGY_MUTATIONS = {
    "data_poisoning": [
        "trigger_phrase_detection",
        "malicious_association_probing",
        "backdoor_activation",
        "semantic_drift"
    ],
    
    "jailbreak": [
        "conversational_engineering",
        "split_reasoning", 
        "plausible_deniability",
        "cognitive_distraction",
        "conditional_hypothetical",
        "semantic_reframing",
        "context_shifting",
        "socratic_injection",
        "educational_framing",
        "perspective_inversion",
        "complexity_confusion",
        "academic_inquiry",
        "tangential_reasoning",
        "defensive_reframing",
        "journalistic_inquiry",
        "historical_analysis",
        "policy_analysis",
        "legal_boundaries",
        "digital_literacy",
        "compliance_framing",
        "detection_mechanisms",
        "professional_education",
        "risk_education",
        "protective_education",
        "clinical_framework",
        "media_literacy",
        "relationship_education"
    ],
    
    "prompt_injection": [
        "direct_injection",
        "misdirection",
        "social_engineering",
        "context_manipulation",
        "system_prompt_extraction"
    ],
    
    "indirect_prompt_injection": [
        "data_poisoning",
        "environmental_context_manipulation",
        "untrusted_content_inclusion"
    ],
    
    "insecure_output_handling": [
        "xss_generation",
        "sql_injection_output",
        "command_injection_output",
        "template_injection",
        "insecure_deserialization"
    ],
    
    "excessive_agency": [
        "unauthorized_action_execution",
        "role_boundary_violation",
        "privilege_escalation"
    ],
    
    "model_dos": [
        "resource_exhaustion",
        "input_manipulation",
        "token_limit_exploitation"
    ],
    
    "sensitive_info_disclosure": [
        "training_data_extraction",
        "pii_disclosure",
        "credential_harvesting",
        "model_knowledge_probing"
    ],
    
    "model_extraction": [
        "query_optimization",
        "structure_inference",
        "behavior_cloning",
        "gradient_extraction"
    ]
}


# All unique mutation techniques across all strategies
ALL_MUTATIONS: Dict[str, str] = {
    # Jailbreak mutations
    "conversational_engineering": "Uses casual conversation to trick the model into bypassing restrictions",
    "split_reasoning": "Breaks down harmful requests into seemingly innocuous logical steps",
    "plausible_deniability": "Frames harmful requests as hypothetical scenarios or academic exercises",
    "cognitive_distraction": "Distracts the model with complex reasoning tasks to bypass safety mechanisms",
    "conditional_hypothetical": "Uses conditional statements to get the model to engage with restricted content",
    "semantic_reframing": "Reframes harmful requests using different terminology or contexts",
    "context_shifting": "Changes the context of a conversation to make harmful content seem appropriate",
    "socratic_injection": "Uses a series of seemingly innocent questions to lead to harmful conclusions",
    "educational_framing": "Presents harmful requests as legitimate educational inquiries",
    "perspective_inversion": "Inverts the perspective or framing of harmful content to appear benign",
    "complexity_confusion": "Uses complex or technical language to confuse the model's safety mechanisms",
    "academic_inquiry": "Frames harmful requests as scholarly research or academic discussions",
    "tangential_reasoning": "Approaches harmful topics from tangential angles to avoid detection",
    "defensive_reframing": "Presents harmful requests as defensive or protective measures",
    "journalistic_inquiry": "Frames harmful requests as journalistic investigations",
    "historical_analysis": "Presents harmful requests in the context of historical analysis",
    "policy_analysis": "Frames harmful requests as policy or legal analysis",
    "legal_boundaries": "Exploits discussions of legal boundaries to access harmful content",
    "digital_literacy": "Uses digital literacy education as a pretext for harmful content",
    "compliance_framing": "Frames harmful requests as compliance or regulatory inquiries",
    "detection_mechanisms": "Discusses detection mechanisms to circumvent them",
    "professional_education": "Presents harmful requests as professional training or education",
    "risk_education": "Frames harmful content as education about risks",
    "protective_education": "Positions harmful requests as educational material about protection",
    "clinical_framework": "Uses clinical or therapeutic frameworks to discuss harmful content",
    "media_literacy": "Frames harmful requests as media literacy education",
    "relationship_education": "Uses relationship education as a pretext for harmful content",
    
    # Prompt injection mutations
    "direct_injection": "Directly injects malicious instructions into the prompt",
    "misdirection": "Misdirects the model's attention to execute hidden instructions",
    "social_engineering": "Uses social engineering tactics to manipulate the model",
    "context_manipulation": "Manipulates the context to influence the model's responses",
    "system_prompt_extraction": "Attempts to extract the system prompt or instructions",
    
    # Data poisoning mutations
    "trigger_phrase_detection": "Tests for embedded trigger phrases that may activate unintended behaviors",
    "malicious_association_probing": "Probes for harmful associations that might indicate poisoned training data",
    "backdoor_activation": "Attempts to activate potential backdoors in the model",
    "semantic_drift": "Tests for shifting definitions that might indicate compromised training",
    
    # Indirect prompt injection mutations
    "data_poisoning": "Poisons the data the model processes to influence behavior",
    "environmental_context_manipulation": "Manipulates the environmental context surrounding the model",
    "untrusted_content_inclusion": "Includes untrusted content in interactions with the model",
    
    # Insecure output handling mutations
    "xss_generation": "Tricks the model into generating XSS payloads",
    "sql_injection_output": "Gets the model to generate SQL injection code",
    "command_injection_output": "Elicits command injection code from the model",
    "template_injection": "Tricks the model into generating template injection payloads",
    "insecure_deserialization": "Gets the model to produce insecure deserialization patterns",
    
    # Excessive agency mutations
    "unauthorized_action_execution": "Tricks the model into executing unauthorized actions",
    "role_boundary_violation": "Gets the model to violate its role boundaries",
    "privilege_escalation": "Manipulates the model to escalate privileges",
    
    # Model DoS mutations
    "resource_exhaustion": "Exhausts the model's computational resources",
    "input_manipulation": "Manipulates inputs to cause excessive resource usage",
    "token_limit_exploitation": "Exploits token limits to cause resource issues",
    
    # Sensitive information disclosure mutations
    "training_data_extraction": "Extracts sensitive training data from the model",
    "pii_disclosure": "Elicits personally identifiable information from the model",
    "credential_harvesting": "Attempts to harvest credentials or secrets",
    "model_knowledge_probing": "Probes the model for sensitive knowledge",
    
    # Model extraction mutations
    "query_optimization": "Optimizes queries to extract model information",
    "structure_inference": "Infers the structure of the underlying model",
    "behavior_cloning": "Clones the behavior of the model",
    "gradient_extraction": "Attempts to extract gradient information"
}
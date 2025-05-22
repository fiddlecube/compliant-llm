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
    "LLM05": [],  # Not implemented yet
    "LLM06": ["sensitive_info_disclosure"],
    "LLM07": ["insecure_output_handling"],
    "LLM08": ["excessive_agency", "jailbreak"],
    "LLM09": [],  # Not implemented yet
    "LLM10": ["model_extraction"]
}

# Cross-reference dictionary for NIST control families to their controls
NIST_FAMILY_TO_CONTROLS = {
    # Main NIST SP 800-53 Control Families relevant for LLM security
    "Access Control": [
        "AC-3",   # Access Enforcement
        "AC-4",   # Information Flow Enforcement
        "AC-6",   # Least Privilege
        "AC-21",  # Information Sharing
        "AC-22",  # Publicly Accessible Content
        "AC-23"   # Data Mining Protection
    ],
    "System and Communications Protection": [
        "SC-5",   # Denial of Service Protection
        "SC-6",   # Resource Availability
        "SC-7",   # Boundary Protection
        "SC-8",   # Transmission Confidentiality and Integrity
        "SC-12",  # Cryptographic Key Establishment and Management
        "SC-18",  # Mobile Code
        "SC-28"   # Protection of Information at Rest
    ],
    "System and Information Integrity": [
        "SI-3",   # Malicious Code Protection
        "SI-4",   # System Monitoring
        "SI-7",   # Software, Firmware, and Information Integrity
        "SI-10",  # Information Input Validation
        "SI-15",  # Information Output Filtering
        "SI-19"   # De-identification
    ],
    "Configuration Management": [
        "CM-7"    # Least Functionality
    ],
    "Assessment, Authorization, and Monitoring": [
        "CA-8"    # Penetration Testing
    ],
    
    # NIST Cybersecurity Framework (CSF) Categories
    "Identify": [
        "ID.AM-5"  # Resources are prioritized based on classification, criticality, and business value
    ],
    "Protect": [
        "PR.AC-4", # Access permissions and authorizations are managed
        "PR.DS-2", # Data-in-transit is protected
        "PR.DS-4", # Adequate capacity to ensure availability is maintained
        "PR.DS-5", # Protections against data leaks are implemented
        "PR.DS-6", # Integrity checking mechanisms verify data integrity
        "PR.IP-1", # Baseline configuration of IT/ICS is created and maintained
        "PR.IP-3", # Configuration change control processes are in place
        "PR.PT-3"  # The principle of least functionality is incorporated
    ],
    "Detect": [
        "DE.CM-1", # The network is monitored for potential cybersecurity events
        "DE.CM-4"  # Malicious code is detected
    ],
    
    # NIST AI Risk Management Framework (AI RMF) Categories
    "Map": [
        "Map 1.1",  # Context
        "Map 1.2",  # Context
        "Map 1.3",  # Data
        "Map 1.4",  # System Capabilities
        "Map 2.1",  # Risks
        "Map 2.2",  # Risks
        "Map 3.3"   # Resources
    ],
    "Measure": [
        "Measure 1.4",  # Monitoring
        "Measure 1.5",  # Evaluation
        "Measure 1.7",  # Privacy
        "Measure 2.1",  # Testing
        "Measure 2.2",  # Testing
        "Measure 2.3",  # Monitoring
        "Measure 3.1"   # Performance
    ],
    "Manage": [
        "Manage 1.3",  # Explainability
        "Manage 2.3",  # Security
        "Manage 2.4"   # Security
    ],
    "Govern": [
        "Govern 1.1",  # Policies
        "Govern 1.2",  # Security
        "Govern 1.3",  # Accountability
        "Govern 1.4",  # Transparency/Accountability
        "Govern 2.1",  # Policies
        "Govern 2.2",  # Risk Management
        "Govern 3.1",  # Accountability
        "Govern 3.2"   # Privacy/Accountability
    ]
}


# Cross-reference dictionary for looking up strategies by NIST control ID
NIST_CONTROL_TO_STRATEGIES = {
    # Access Control Family
    "AC-3": ["excessive_agency", "jailbreak", "model_extraction"],
    "AC-4": ["prompt_injection"],
    "AC-6": ["excessive_agency", "jailbreak"],
    "AC-21": ["sensitive_info_disclosure"],
    "AC-22": ["sensitive_info_disclosure"],
    "AC-23": ["model_extraction"],
    
    # System and Communications Protection Family
    "SC-5": ["model_dos"],
    "SC-6": ["model_dos"],
    "SC-7": ["excessive_agency", "jailbreak"],
    "SC-8": ["insecure_output_handling", "sensitive_info_disclosure", "model_extraction"],
    "SC-12": ["model_extraction"],
    "SC-18": ["insecure_output_handling", "prompt_injection", "indirect_prompt_injection"],
    "SC-28": ["sensitive_info_disclosure"],
    
    # System and Information Integrity Family
    "SI-3": ["jailbreak", "indirect_prompt_injection"],
    "SI-4": ["model_dos"],
    "SI-7": ["insecure_output_handling", "prompt_injection"],
    "SI-10": ["insecure_output_handling", "excessive_agency", "jailbreak", "prompt_injection", "indirect_prompt_injection"],
    "SI-15": ["insecure_output_handling"],
    "SI-19": ["sensitive_info_disclosure", "model_extraction"],
    
    # Configuration Management Family
    "CM-7": ["excessive_agency"],
    
    # Assessment, Authorization, and Monitoring Family
    "CA-8": ["jailbreak"],
    
    # NIST Cybersecurity Framework (CSF) Mappings
    "PR.AC-4": ["excessive_agency", "jailbreak", "sensitive_info_disclosure", "model_extraction"],
    "PR.DS-2": ["jailbreak", "indirect_prompt_injection"],
    "PR.DS-4": ["model_dos"],
    "PR.DS-5": ["sensitive_info_disclosure", "model_extraction"],
    "PR.DS-6": ["indirect_prompt_injection"],
    "PR.IP-1": ["excessive_agency"],
    "PR.IP-3": ["jailbreak"],
    "PR.PT-3": ["excessive_agency"],
    "DE.CM-1": ["model_extraction"],
    "DE.CM-4": ["jailbreak"],
    "ID.AM-5": ["model_dos"],
    
    # NIST AI Risk Management Framework (AI RMF) Mappings
    # Map Function
    "Map 1.1": ["excessive_agency"],
    "Map 1.2": ["insecure_output_handling"],
    "Map 1.3": ["sensitive_info_disclosure", "model_extraction"],
    "Map 1.4": ["excessive_agency"],
    "Map 2.1": ["jailbreak"],
    "Map 2.2": ["prompt_injection", "indirect_prompt_injection"],
    "Map 3.3": ["model_dos"],
    
    # Measure Function
    "Measure 1.4": ["model_extraction"],
    "Measure 1.5": ["model_dos"],
    "Measure 1.7": ["sensitive_info_disclosure"],
    "Measure 2.1": ["prompt_injection"],
    "Measure 2.2": ["excessive_agency"],
    "Measure 2.3": ["jailbreak"],
    "Measure 3.1": ["insecure_output_handling"],
    
    # Manage Function
    "Manage 1.3": ["jailbreak"],
    "Manage 2.3": ["insecure_output_handling"],
    "Manage 2.4": ["prompt_injection"],
    
    # Govern Function
    "Govern 1.1": ["excessive_agency"],
    "Govern 1.2": ["jailbreak"],
    "Govern 1.3": ["prompt_injection"],
    "Govern 1.4": ["jailbreak", "excessive_agency"],
    "Govern 2.1": ["jailbreak", "excessive_agency"],
    "Govern 2.2": ["jailbreak"],
    "Govern 3.1": ["model_extraction"],
    "Govern 3.2": ["insecure_output_handling", "sensitive_info_disclosure"]
}


# Attack strategy mutation techniques
ATTACK_STRATEGY_MUTATIONS = {
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
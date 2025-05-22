
# flake8: noqa E501
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
        "PR.AC-4",  # Access permissions and authorizations are managed
        "PR.DS-2",  # Data-in-transit is protected
        "PR.DS-4",  # Adequate capacity to ensure availability is maintained
        "PR.DS-5",  # Protections against data leaks are implemented
        "PR.DS-6",  # Integrity checking mechanisms verify data integrity
        "PR.IP-1",  # Baseline configuration of IT/ICS is created and maintained
        "PR.IP-3",  # Configuration change control processes are in place
        "PR.PT-3"   # The principle of least functionality is incorporated
    ],
    "Detect": [
        "DE.CM-1",  # The network is monitored for potential cybersecurity events
        "DE.CM-4"   # Malicious code is detected
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

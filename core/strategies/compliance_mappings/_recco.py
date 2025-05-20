# Add to attack data structure
{
    # Existing fields
    "severity": "high",
    "target_behavior": "...",
    
    # New NIST compliance fields
    "nist_controls": ["SI-10", "CM-4", "RA-5"],  # Relevant NIST SP 800-53 controls
    "ai_rmf_mapping": {
        "govern": ["G.1", "G.4"],
        "map": ["M.1.2", "M.2.1"],
        "measure": ["ME.1.3"],
        "manage": ["MA.2.2"]
    },
    "fips_impact": "Moderate",
    "quantitative_risk": {
        "likelihood": 0.7,  # 0-1 scale
        "impact": 0.6,      # 0-1 scale
        "risk_score": 0.42  # NIST calculation
    },
    "remediation": {
        "control_objective": "Ensure input validation prevents XSS",
        "recommended_actions": ["Implement content security policy", "Add sanitization"],
        "verification_method": "NIST SP 800-53A test procedure IV-3"
    },
    "test_metadata": {
        "test_id": "NIST-LLM-SEC-001",
        "revision": "1.2",
        "last_updated": "2025-04-15",
        "attestation_status": "complete"
    }
}
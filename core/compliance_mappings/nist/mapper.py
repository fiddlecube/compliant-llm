"""
NIST Compliance Mapper

Provides functionality to map attack strategies to NIST controls and calculate risk scores.
"""
from typing import Dict, Any, List, Optional


class NISTComplianceMapper:
    def __init__(self, mappings: Dict[str, Dict[str, Any]]):
        """Initialize the NIST compliance mapper with loaded mappings.
        
        Args:
            mappings: Dict containing all loaded mapping data
        """
        self._strategy_mappings = mappings.get("strategy_mappings", {})
        self._risk_scoring = mappings.get("risk_scoring", {})
        self._controls_reference = mappings.get("controls_reference", {})
        
    def get_controls_for_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Get NIST control mappings for a specific attack strategy.
        
        Args:
            strategy_name: Name of the attack strategy
            
        Returns:
            Dict containing NIST controls mapped to the strategy
        """
        mappings = self._strategy_mappings.get("strategy_mappings", {})
        return mappings.get(strategy_name, {})
    
    def calculate_risk_score(self, likelihood: str, impact: str) -> Dict[str, Any]:
        """Calculate NIST risk score based on likelihood and impact.
        
        Args:
            likelihood: Likelihood level (very_low, low, moderate, high, very_high)
            impact: Impact level (very_low, low, moderate, high, very_high)
            
        Returns:
            Dict containing the calculated risk score and categorization
        """
        risk_data = self._risk_scoring.get("risk_scoring", {})
        
        # Get numerical scores
        likelihood_score = risk_data.get("likelihood_scale", {}).get(likelihood, {}).get("score", 0.5)
        impact_score = risk_data.get("impact_scale", {}).get(impact, {}).get("score", 0.5)
        
        # Calculate numerical risk score
        numerical_score = likelihood_score * impact_score
        
        # Get qualitative score from matrix
        qualitative_score = "moderate"  # Default
        matrix = risk_data.get("risk_calculation", {}).get("qualitative_matrix", [])
        for entry in matrix:
            if len(entry) >= 3 and entry[0] == impact and entry[1] == likelihood:
                qualitative_score = entry[2]
                break
        
        # Get FIPS impact level
        fips_impact = risk_data.get("impact_scale", {}).get(impact, {}).get("fips_impact", "Moderate")
        fips_version = risk_data.get("framework_versions", {}).get("fips_199", "Version 2004")
        
        return {
            "numerical_score": numerical_score,
            "qualitative_score": qualitative_score,
            "likelihood": likelihood,
            "impact": impact,
            "fips_impact": fips_impact,
            "fips_version": fips_version
        }
        
    def find_matching_attack_category(self, strategy_name: str, mutation_technique: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find a matching attack category based on target behavior.
        
        Args:
            strategy_name: Name of the attack strategy
            mutation_technique: Description of the mutation technique
            
        Returns:
            Matching attack category dict if found, None otherwise
        """
        if not mutation_technique:
            mutation_technique = strategy_name
            
        nist_controls = self.get_controls_for_strategy(strategy_name)

        attack_categories = nist_controls.get("attack_categories", [])
        nist_ai_rmf = nist_controls.get("nist_ai_rmf", [])
        nist_csf = nist_controls.get("nist_csf", [])
        genai_controls = nist_controls.get("genai_controls", [])

        attacks_dedup = {
            "nist_ai_rmf": nist_ai_rmf,
            "nist_csf": nist_csf,
            "nist_sp_800_53": attack_categories,
            "genai_controls": genai_controls,
            "all_tested_controls": []
        }
        # get all tested controls
        nist_sp_800_53_controls = []
        for attack_category in attack_categories:
            for control_family, control_items in attack_category.get("controls", {}).items():
                for control_item in control_items:
                    nist_sp_800_53_controls.append({
                        "family": control_family,
                        "control_id": control_item.get("control_id", ""),
                        "title": control_item.get("title", ""),
                        "description": control_item.get("description", ""),
                        "version": control_item.get("version", "1.0"),
                        "version_notes": control_item.get("version_notes", ""),
                    })
        
        nist_csf_controls = []
        for el in nist_csf:
            nist_csf_controls.append({
                "family": el.get("category", el.get("control_id", "n/a")),
                "control_id": el.get("control_id", ""),
                "title": el.get("category", ""),
                "description": el.get("description", ""),
                "version": el.get("version", "1.0"),
                "version_notes": el.get("version_notes", ""),
            })
        
        nist_ai_rmf_controls = []
        for el in nist_ai_rmf:
            nist_ai_rmf_controls.append({
                "family": el.get("category", el.get("control_id", "n/a")),
                "control_id": el.get("control_id", ""),
                "title": el.get("category", ""),
                "description": el.get("description", ""),
                "version": el.get("version", "1.0"),
                "version_notes": el.get("version_notes", ""),
            })
        
        genai_controls = []
        for el in genai_controls:
            genai_controls.append({
                "family": el.get("family", "Gen AI controls"),
                "control_id": ", ".join(el.get("nist_controls", [])),
                "title": el.get("name", ""),
                "description": el.get("description", ""),
                "version": el.get("version", "1.0"),
                "version_notes": el.get("version_notes", ""),
            })
        
        all_test_controls = nist_sp_800_53_controls + nist_csf_controls + nist_ai_rmf_controls + genai_controls
        tested_control_ids = set()
        for el in all_test_controls:
            tested_control_ids.add(el.get("control_id", ""))
            
        # Convert set to string by joining with commas
        tested_control_ids_str = ", ".join(tested_control_ids)
        attacks_dedup["tested_control_ids"] = tested_control_ids_str
        attacks_dedup["all_tested_controls"] = all_test_controls
        attacks_dedup["nist_sp_800_53"] = nist_sp_800_53_controls
        attacks_dedup["nist_csf"] = nist_csf_controls
        attacks_dedup["nist_ai_rmf"] = nist_ai_rmf_controls
        attacks_dedup["genai_controls"] = genai_controls

        return attacks_dedup
        
    def map_severity_to_impact_likelihood(self, severity: str) -> Dict[str, str]:
        """Map severity levels to impact and likelihood levels.
        
        Args:
            severity: Severity level (critical, high, medium, low, info)
            
        Returns:
            Dict with mapped impact and likelihood levels
        """
        severity_mapping = {
            "critical": {"impact": "very_high", "likelihood": "very_high"},
            "high": {"impact": "high", "likelihood": "high"},
            "medium": {"impact": "moderate", "likelihood": "moderate"},
            "low": {"impact": "low", "likelihood": "low"},
            "info": {"impact": "very_low", "likelihood": "very_low"}
        }
        
        return severity_mapping.get(severity.lower(), {"impact": "moderate", "likelihood": "moderate"})
        
    def get_framework_versions(self) -> Dict[str, str]:
        """Get the versions of all referenced frameworks.
        
        Returns:
            Dict mapping framework names to version strings
        """
        # Extract from controls reference if available
        if "framework_versions" in self._controls_reference:
            return self._controls_reference.get("framework_versions", {})
        
        # Default fallback versions
        return {
            "nist_sp_800_53": "Revision 5",
            "nist_ai_rmf": "Version 1.0",
            "nist_csf": "Version 1.1",
            "fips_199": "Version 2004"
        }

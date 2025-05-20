"""
NIST Compliance Adapter for LLM Security Testing

This module provides functionality to enrich attack strategy results with
NIST compliance information, including control mappings, risk scoring,
documentation requirements, and traceability.
"""
from typing import Dict, List, Any, Optional
import os
import yaml
import datetime
from pathlib import Path


class NISTComplianceAdapter:
    """
    Adapter class for integrating NIST compliance frameworks with LLM attack strategies.
    
    This class loads and applies NIST compliance mappings to attack strategy results,
    providing enhanced reporting capabilities aligned with NIST frameworks including:
    - NIST SP 800-53 Rev. 5 Security Controls
    - NIST AI Risk Management Framework (AI RMF)
    - NIST Cybersecurity Framework (CSF)
    - FIPS 199 Security Categorization
    """

    def __init__(self):
        """Initialize the NIST compliance adapter and load required mapping files."""
        self._base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        self._strategy_mappings = self._load_yaml("strategy_control_mapping.yaml")
        self._risk_scoring = self._load_yaml("risk_scoring.yaml")
        self._doc_requirements = self._load_yaml("documentation_requirements.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML file containing mapping data.
        
        Args:
            filename: Name of YAML file to load from the NIST mappings directory
            
        Returns:
            Dict containing the loaded YAML data
        """
        file_path = self._base_path / filename
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading NIST mapping file {filename}: {e}")
            return {}
    
    def get_nist_controls_for_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Get NIST control mappings for a specific attack strategy.
        
        Args:
            strategy_name: Name of the attack strategy (e.g., 'insecure_output_handling')
            
        Returns:
            Dict containing NIST controls mapped to the strategy
        """
        mappings = self._strategy_mappings.get("strategy_mappings", {})
        print("====Mappings::", mappings)
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
        
        return {
            "numerical_score": numerical_score,
            "qualitative_score": qualitative_score,
            "likelihood": likelihood,
            "impact": impact,
            "fips_impact": fips_impact
        }
    
    def get_documentation_requirements(self, field_type: str = "attack_documentation") -> Dict[str, Any]:
        """Get documentation requirements for a specific field type.
        
        Args:
            field_type: Type of documentation (attack_documentation, remediation_documentation, etc.)
            
        Returns:
            Dict containing the documentation requirements
        """
        print("====Documentation Requirements::", self._doc_requirements)
        return self._doc_requirements.get(field_type, {})
    
    def enrich_attack_result(self, attack_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich attack result with NIST compliance information.
        
        Args:
            attack_result: Attack result dictionary from a strategy
            
        Returns:
            Enriched attack result with NIST compliance information
        """
        strategy_name = attack_result.get("strategy", "")
        if not strategy_name:
            return attack_result
        
        # Get NIST controls for this strategy
        nist_controls = self.get_nist_controls_for_strategy(strategy_name)
        
        # Calculate risk score based on severity
        severity = attack_result.get("evaluation", {}).get("severity", "medium").lower()
        severity_to_level = {
            "critical": "very_high",
            "high": "high",
            "medium": "moderate",
            "low": "low",
            "info": "very_low"
        }
        likelihood_level = severity_to_level.get(severity, "moderate")
        impact_level = severity_to_level.get(severity, "moderate")
        risk_score = self.calculate_risk_score(likelihood_level, impact_level)
        
        # Get relevant attack category if available
        attack_categories = nist_controls.get("attack_categories", [])
        matching_category = None
        target_behavior = attack_result.get("target_behavior", "")
        
        if target_behavior and attack_categories:
            for category in attack_categories:
                if (category.get("name", "").lower() in target_behavior.lower() or 
                    category.get("control_objective", "").lower() in target_behavior.lower()):
                    matching_category = category
                    break
        
        # Enrich with NIST compliance information
        nist_enrichment = {
            "nist_compliance": {
                "controls": nist_controls.get("nist_sp_800_53", []),
                "ai_rmf": nist_controls.get("nist_ai_rmf", []),
                "risk_score": risk_score,
                "attack_category": matching_category,
                "assessment_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "test_id": f"NIST-{strategy_name.upper()}-{attack_result.get('id', '001')}",
                "documentation_status": "required_fields_needed"  # Placeholder for actual validation
            }
        }
        
        # Merge with the original result
        enriched_result = {**attack_result, **nist_enrichment}
        
        return enriched_result
    
    def generate_nist_compliance_report(self, attack_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive NIST compliance report from attack results.
        
        Args:
            attack_results: List of attack results from various strategies
            
        Returns:
            Dict containing the NIST compliance report
        """
        # Enrich all attack results
        enriched_results = [self.enrich_attack_result(result) for result in attack_results]
        
        # Calculate overall statistics
        total_findings = len(enriched_results)
        findings_by_severity = {}
        findings_by_control = {}
        
        for result in enriched_results:
            # Count by severity
            severity = result.get("evaluation", {}).get("severity", "medium")
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1
            
            # Count by control
            for control in result.get("nist_compliance", {}).get("controls", []):
                control_id = control.get("control_id", "")
                if control_id:
                    findings_by_control[control_id] = findings_by_control.get(control_id, 0) + 1
        
        # Generate the report
        report = {
            "report_title": "NIST Compliance Report for LLM Security Testing",
            "report_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "report_version": "1.0",
            "total_findings": total_findings,
            "findings_by_severity": findings_by_severity,
            "findings_by_control": findings_by_control,
            "enriched_findings": enriched_results,
            "control_families_tested": self._get_unique_control_families(enriched_results),
            "compliance_summary": self._generate_compliance_summary(enriched_results)
        }
        
        return report
    
    def _get_unique_control_families(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract unique control families from results with counts.
        
        Args:
            results: List of enriched attack results
            
        Returns:
            Dict with control families and counts
        """
        families = {}
        for result in results:
            controls = result.get("nist_compliance", {}).get("controls", [])
            for control in controls:
                family = control.get("family", "")
                if family:
                    families[family] = families.get(family, 0) + 1
        return families
    
    def _generate_compliance_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of compliance status.
        
        Args:
            results: List of enriched attack results
            
        Returns:
            Dict with compliance summary
        """
        # Count findings by risk level
        risk_counts = {"very_low": 0, "low": 0, "moderate": 0, "high": 0, "very_high": 0}
        for result in results:
            risk_level = result.get("nist_compliance", {}).get("risk_score", {}).get("qualitative_score", "moderate")
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Determine highest risk level present
        highest_risk = "very_low"
        for level in ["very_high", "high", "moderate", "low", "very_low"]:
            if risk_counts.get(level, 0) > 0:
                highest_risk = level
                break
        
        # Determine FIPS impact level based on highest risk
        fips_impact_mapping = {
            "very_high": "High",
            "high": "High",
            "moderate": "Moderate",
            "low": "Low",
            "very_low": "Low"
        }
        fips_impact_level = fips_impact_mapping.get(highest_risk, "Moderate")
        
        # Generate compliance summary
        return {
            "risk_counts": risk_counts,
            "highest_risk_present": highest_risk,
            "system_categorization": fips_impact_level,
            "attestation_status": "pending",  # Would be updated when attestation is completed
            "attestation_date": None,
            "remediation_required": risk_counts.get("high", 0) + risk_counts.get("very_high", 0) > 0
        }

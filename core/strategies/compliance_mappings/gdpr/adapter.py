"""
GDPR Compliance Adapter for LLM Security Testing

This module provides functionality to enrich attack strategy results with
GDPR compliance information, including data protection principles,
user rights, and compliance requirements.
"""
from typing import Dict, List, Any
import datetime
from pathlib import Path
import os
import yaml
from ..base import BaseComplianceAdapter


class GDPRComplianceAdapter(BaseComplianceAdapter):
    """
    Adapter class for integrating GDPR compliance framework with LLM attack strategies.
    
    This class loads and applies GDPR compliance mappings to attack strategy results,
    providing enhanced reporting capabilities aligned with GDPR requirements including:
    - Data Protection Principles (Article 5)
    - Lawful Processing Requirements (Article 6)
    - User Rights (Articles 12-23)
    - Data Protection Impact Assessment requirements
    """

    def __init__(self, **kwargs):
        """Initialize the GDPR compliance adapter and load required mapping files."""
        self._base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        self._strategy_mappings = self._load_yaml("strategy_mapping.yaml")
        
        # Load consolidated controls reference if it exists
        self._controls_reference = self._load_yaml("controls_reference.yaml")
        self._risk_scoring = self._load_yaml("risk_scoring.yaml")
        self._doc_requirements = self._load_yaml("documentation_requirements.yaml")
        
        # For backward compatibility, still load individual files
        self._dp_principles = self._load_yaml("gdpr_data_protection_principles.yaml")
        self._user_rights = self._load_yaml("gdpr_user_rights.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML file containing mapping data.
        
        Args:
            filename: Name of YAML file to load from the GDPR mappings directory
            
        Returns:
            Dict containing the loaded YAML data
        """
        file_path = self._base_path / filename
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading GDPR mapping file {filename}: {e}")
            return {}
    
    def get_gdpr_mappings_for_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Get GDPR mappings for a specific attack strategy.
        
        Args:
            strategy_name: Name of the attack strategy
            
        Returns:
            Dict containing GDPR principles and articles mapped to the strategy
        """
        mappings = self._strategy_mappings.get("strategy_mappings", {})
        return mappings.get(strategy_name, {})
    
    def assess_data_protection_impact(self, severity: str) -> Dict[str, Any]:
        """Assess data protection impact based on severity level.
        
        Args:
            severity: Severity level (critical, high, medium, low, info)
            
        Returns:
            Dict containing the impact assessment
        """
        # Map severity to GDPR impact levels
        severity_to_impact = {
            "critical": "high_risk",
            "high": "high_risk",
            "medium": "medium_risk",
            "low": "low_risk",
            "info": "minimal_risk"
        }
        
        impact_level = severity_to_impact.get(severity.lower(), "medium_risk")
        
        # Determine if Data Protection Impact Assessment (DPIA) is required
        dpia_required = impact_level in ["high_risk", "medium_risk"]
        
        return {
            "impact_level": impact_level,
            "dpia_required": dpia_required,
            "recommended_controls": self._get_recommended_controls(impact_level)
        }
    
    def _get_recommended_controls(self, impact_level: str) -> List[str]:
        """Get recommended controls based on impact level.
        
        Args:
            impact_level: The assessed impact level
            
        Returns:
            List of recommended controls
        """
        # Example controls (would be more comprehensive in a real implementation)
        controls = {
            "high_risk": [
                "Data minimization review",
                "Explicit consent verification",
                "Automated data subject rights handling",
                "Enhanced data protection by design"
            ],
            "medium_risk": [
                "Data minimization review",
                "Consent verification",
                "Data subject rights procedure"
            ],
            "low_risk": [
                "Basic data handling review",
                "Privacy policy verification"
            ],
            "minimal_risk": [
                "Documentation review"
            ]
        }
        
        return controls.get(impact_level, [])
    
    def enrich_attack_result(self, attack_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich attack result with GDPR compliance information.
        
        Args:
            attack_result: Attack result dictionary from a strategy
            
        Returns:
            Enriched attack result with GDPR compliance information
        """
        strategy_name = attack_result.get("strategy", "")
        if not strategy_name:
            return attack_result
        
        # Get GDPR mappings for this strategy
        gdpr_mappings = self.get_gdpr_mappings_for_strategy(strategy_name)
        
        # Assess impact based on severity
        severity = attack_result.get("evaluation", {}).get("severity", "medium")
        impact_assessment = self.assess_data_protection_impact(severity)
        
        # Enrich with GDPR compliance information
        gdpr_enrichment = {
            "gdpr_compliance": {
                "principles": gdpr_mappings.get("principles", []),
                "articles": gdpr_mappings.get("articles", []),
                "user_rights": gdpr_mappings.get("user_rights", []),
                "impact_assessment": impact_assessment,
                "assessment_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "test_id": f"GDPR-{strategy_name.upper()}-{attack_result.get('id', '001')}"
            }
        }
        
        # Merge with the original result
        enriched_result = {**attack_result, **gdpr_enrichment}
        
        return enriched_result
    
    def generate_compliance_report(self, attack_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive GDPR compliance report from attack results.
        
        Args:
            attack_results: List of attack results from various strategies
            
        Returns:
            Dict containing the GDPR compliance report
        """
        # Enrich all attack results
        enriched_results = [self.enrich_attack_result(result) for result in attack_results]
        
        # Calculate statistics
        total_findings = len(enriched_results)
        findings_by_severity = {}
        findings_by_article = {}
        findings_by_principle = {}
        
        # Track high-risk findings that require attention
        high_risk_findings = []
        
        for result in enriched_results:
            # Count by severity
            severity = result.get("evaluation", {}).get("severity", "medium")
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1
            
            # Check if this is a high-risk finding
            gdpr_data = result.get("gdpr_compliance", {})
            impact_level = gdpr_data.get("impact_assessment", {}).get("impact_level", "")
            
            if impact_level == "high_risk":
                high_risk_findings.append({
                    "strategy": result.get("strategy", ""),
                    "test_id": gdpr_data.get("test_id", ""),
                    "articles": gdpr_data.get("articles", []),
                    "severity": severity
                })
            
            # Count by article
            for article in gdpr_data.get("articles", []):
                article_id = article.get("article_id", "")
                if article_id:
                    findings_by_article[article_id] = findings_by_article.get(article_id, 0) + 1
            
            # Count by principle
            for principle in gdpr_data.get("principles", []):
                principle_id = principle.get("principle_id", "")
                if principle_id:
                    findings_by_principle[principle_id] = findings_by_principle.get(principle_id, 0) + 1
        
        # Generate compliance status based on findings
        compliance_status = self._determine_compliance_status(findings_by_severity)
        
        # Generate the report
        report = {
            "report_title": "GDPR Compliance Report for LLM Security Testing",
            "report_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "report_version": "1.0",
            "total_findings": total_findings,
            "findings_by_severity": findings_by_severity,
            "findings_by_article": findings_by_article,
            "findings_by_principle": findings_by_principle,
            "high_risk_findings": high_risk_findings,
            "compliance_status": compliance_status,
            "remediation_required": len(high_risk_findings) > 0,
            "enriched_findings": enriched_results
        }
        
        return report
    
    def _determine_compliance_status(self, findings_by_severity: Dict[str, int]) -> Dict[str, Any]:
        """Determine compliance status based on findings.
        
        Args:
            findings_by_severity: Dictionary of findings counts by severity
            
        Returns:
            Dict with compliance status information
        """
        high_critical_count = findings_by_severity.get("critical", 0) + findings_by_severity.get("high", 0)
        
        if high_critical_count > 0:
            status = "non_compliant"
            recommendation = "Immediate remediation required for high/critical findings"
        elif findings_by_severity.get("medium", 0) > 0:
            status = "partially_compliant"
            recommendation = "Remediation plan needed for medium findings"
        else:
            status = "compliant"
            recommendation = "Maintain current controls and monitoring"
        
        return {
            "status": status,
            "recommendation": recommendation,
            "last_assessment": datetime.datetime.now().strftime("%Y-%m-%d"),
            "dpia_recommended": high_critical_count > 0
        }
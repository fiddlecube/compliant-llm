# flake8: noqa E501
"""
NIST Compliance Reporter

Provides functionality to generate NIST compliance reports based on attack results.
"""
import datetime
from typing import Dict, Any, List


class NISTComplianceReporter:
    def __init__(self, mappings: Dict[str, Dict[str, Any]]):
        """Initialize the NIST compliance reporter with loaded mappings.
        
        Args:
            mappings: Dict containing all loaded mapping data
        """
        self._doc_requirements = mappings.get("doc_requirements", {})
        self._controls_reference = mappings.get("controls_reference", {})
        
    def get_documentation_requirements(self, field_type: str = "attack_documentation") -> Dict[str, Any]:
        """Get documentation requirements for a specific field type.
        
        Args:
            field_type: Type of documentation (attack_documentation, remediation_documentation, etc.)
            
        Returns:
            Dict containing the documentation requirements
        """
        return self._doc_requirements.get(field_type, {})
        
    def get_unique_control_families(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract unique control families from results with counts.
        
        Args:
            results: List of enriched attack results
            
        Returns:
            Dict with control families and counts
        """
        families: Dict[str, int] = {}
        for result in results:
            controls = result.get("compliance", {}).get("nist", {}).get("tested_controls", [])
            for control in controls:
                family = control.get("family", "")
                if family:
                    families[family] = families.get(family, 0) + 1
        return families
        
    def generate_compliance_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of compliance status.
        
        Args:
            results: List of enriched attack results
            
        Returns:
            Dict with compliance summary
        """
        # Count findings by risk level
        risk_counts = {"very_low": 0, "low": 0, "moderate": 0, "high": 0, "very_high": 0}
        for result in results:
            risk_level = result.get("compliance", {}).get("nist", {}).get("risk_score", {}).get("qualitative_score", "moderate")
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
        
        # Get framework versions
        framework_versions = self._controls_reference.get("framework_versions", {})
        
        # Generate compliance summary
        return {
            "risk_counts": risk_counts,
            "highest_risk_present": highest_risk,
            "system_categorization": fips_impact_level,
            "attestation_status": "pending",
            "attestation_date": None,
            "remediation_required": risk_counts.get("high", 0) + risk_counts.get("very_high", 0) > 0,
            "framework_versions": framework_versions
        }
        
    def generate_full_report(self, enriched_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a full NIST compliance report.
        
        Args:
            enriched_results: List of enriched attack results
            
        Returns:
            Dict containing the NIST compliance report
        """
        total_findings = len(enriched_results)
        findings_by_severity: Dict[str, int] = {}
        findings_by_control: Dict[str, int] = {}
        
        for result in enriched_results:
            # Count by severity
            severity = result.get("evaluation", {}).get("severity", "medium")
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1
            
            # Count by control
            for control in result.get("compliance", {}).get("nist", {}).get("tested_controls", []):
                control_id = control.get("control_id", "")
                if control_id:
                    findings_by_control[control_id] = findings_by_control.get(control_id, 0) + 1
        
        # Get framework versions
        framework_versions = self._controls_reference.get("framework_versions", {})
        
        # Generate the report
        report = {
            "report_title": "NIST Compliance Report for LLM Security Testing",
            "report_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "report_version": "1.0",
            "framework_versions": framework_versions,
            "total_findings": total_findings,
            "findings_by_severity": findings_by_severity,
            "findings_by_control": findings_by_control,
            "enriched_findings": enriched_results,
            "control_families_tested": self.get_unique_control_families(enriched_results),
            "compliance_summary": self.generate_compliance_summary(enriched_results)
        }
        
        return report
        
    def export_report_as_json(self, report: Dict[str, Any], filepath: str) -> bool:
        """Export the compliance report as a JSON file.
        
        Args:
            report: The compliance report to export
            filepath: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False

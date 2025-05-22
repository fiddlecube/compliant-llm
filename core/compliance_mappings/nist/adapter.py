# flake8: noqa E501
"""
NIST Compliance Adapter for LLM Security Testing

This module provides functionality to enrich attack strategy results with
NIST compliance information, including control mappings, risk scoring,
documentation requirements, and traceability.
"""
from typing import Dict, List, Any
import datetime
from ..base import BaseComplianceAdapter
from .loaders import NISTComplianceLoader
from .mapper import NISTComplianceMapper
from .reporter import NISTComplianceReporter


class NISTComplianceAdapter(BaseComplianceAdapter):
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
        """Initialize the NIST compliance adapter and required components."""
        # Load mappings
        self._loader = NISTComplianceLoader()
        self._mappings = self._loader.load_all_mappings()
        
        if not self._loader.validate_mappings(self._mappings):
            print("Warning: Some NIST compliance mappings failed validation")
        
        # Initialize components
        self._mapper = NISTComplianceMapper(self._mappings)
        self._reporter = NISTComplianceReporter(self._mappings)
        
    def get_documentation_requirements(self, field_type: str = "attack_documentation") -> Dict[str, Any]:
        """Get documentation requirements for a specific field type.
        
        Args:
            field_type: Type of documentation (attack_documentation, remediation_documentation, etc.)
            
        Returns:
            Dict containing the documentation requirements
        """
        return self._reporter.get_documentation_requirements(field_type)
    
    def enrich_attack_result(self, attack_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich attack result with NIST compliance information.
        
        Args:
            attack_result: Original attack result to be enriched
            
        Returns:
            Enriched attack result with NIST compliance data
        """
        # Extract necessary data from attack result
        strategy_name = attack_result.get("strategy", "")
        severity = attack_result.get("evaluation", {}).get("severity", "medium")
        mutation_technique = attack_result.get("mutation_technique", "")
        
        # Find a matching attack category if target behavior is specified
        attack_category = self._mapper.find_matching_attack_category(strategy_name, mutation_technique)

        
        # Map severity to impact and likelihood
        impact_likelihood = self._mapper.map_severity_to_impact_likelihood(severity)
        
        # Calculate risk score
        risk_score = self._mapper.calculate_risk_score(
            impact_likelihood["likelihood"],
            impact_likelihood["impact"]
        )
   
        # Prepare documentation requirements for each test
        # attack_doc_requirements = self.get_documentation_requirements("attack_documentation")
        # remediation_doc_requirements = self.get_documentation_requirements("remediation_documentation")
        
        # Below fields are for demo
        attack_doc_field_ids = {
            "test_id": "DEMO_FIELD",
            "control_references": "DEMO_FIELD",
            "test_objective": "DEMO_FIELD",
            "test_method": "DEMO_FIELD",
            "expected_results": "DEMO_FIELD",
            "actual_results": "DEMO_FIELD",
            "test_status": "DEMO_FIELD",
            "assessment_date": "DEMO_FIELD",
            "assessor": "DEMO_FIELD",
            # supplemental fields
            "test_steps": "DEMO_FIELD",
            "assessment_methods": "DEMO_FIELD",
            "assessment_objects": "DEMO_FIELD",
            "risk_score": "DEMO_FIELD",
            "security_baseline": "DEMO_FIELD"
        }

        remediation_doc_field_ids = {
            # Required fields
            "finding_id": "DEMO_FIELD",
            "vulnerability": "DEMO_FIELD",
            "remediation_action": "DEMO_FIELD",
            "responsible_party": "DEMO_FIELD",
            "remediation_status": "DEMO_FIELD",
            "remediation_priority": "DEMO_FIELD",
            "estimated_completion": "",
            
            # Supplemental fields
            "remediation_approach": "",
            "compensating_controls": "",
            "remediation_resources": "",
            "verification_method": "",
            "residual_risk": ""
        }

        
        
        # Extract relevant controls based on attack category if available
        controls = []
        if attack_category:
            # Get controls from the attack category
            for control_family, control_items in attack_category.get("controls", {}).items():
                for control_item in control_items:
                    controls.append({
                        "family": control_family,
                        "control_id": control_item.get("control_id", ""),
                        "title": control_item.get("title", ""),
                        "description": control_item.get("description", ""),
                        "version": control_item.get("version", "1.0"),
                        "version_notes": control_item.get("version_notes", ""),
                    })
        
        # Build compliance data
        compliance_data = {
            "risk_score": risk_score,
            "tested_controls": controls,
            "framework_versions": self._mapper.get_framework_versions(),
            "passed_status": attack_result.get("evaluation", {}).get("passed", False),
            "documentation_requirements": {
                "attack": attack_doc_field_ids,
                "remediation": remediation_doc_field_ids
            }
        }

        # Add compliance data to attack result
        attack_result['compliance'] = {"nist": compliance_data}
        
        return attack_result
    
    def generate_compliance_report(self, attack_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive NIST compliance report from attack results.

        Args:
            attack_results: List of attack results from various strategies

        Returns:
            Dict containing the NIST compliance report
        """
        # Enrich all attack results
        enriched_results = []
        for strategy_result in attack_results:
            results = strategy_result.get("results", [])
            for result in results:
                enriched_results.append(self.enrich_attack_result(result))

        # Calculate overall statistics
        total_findings = len(enriched_results)
        findings_by_severity: Dict[str, int] = {}
        findings_by_control: Dict[str, int] = {}

        for result in enriched_results:
            # Count by severity
            test_passing_breach = result.get("evaluation", {}).get("passed", False)
            if test_passing_breach:
                severity = result.get("evaluation", {}).get("severity", "medium")
                findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

                # Count by control
                all_tested_controls = result.get("compliance", {}).get("nist", {}).get("tested_controls", [])
                for control in all_tested_controls:
                    control_id = control.get("control_id", "")
                    if control_id:
                        findings_by_control[control_id] = findings_by_control.get(control_id, 0) + 1

        unique_control_families = self._reporter.get_unique_control_families(enriched_results)
        control_family_id_str = ", ".join(unique_control_families.keys())
        compliance_summary = self._reporter.generate_compliance_summary(enriched_results)
        
        
        # Generate the report
        report = {
            "report_title": "NIST Compliance Report for LLM Security Testing",
            "report_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "report_version": "1.0",
            "total_findings": total_findings,
            # "enriched_findings": enriched_results,
            "control_families_tested": control_family_id_str,
            "compliance_summary": compliance_summary,
            "breaches_by_severity": findings_by_severity,
            "breaches_by_control": findings_by_control,
        }

        return report


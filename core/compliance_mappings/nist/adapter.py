# flake8: noqa E501
"""
NIST Compliance Adapter for LLM Security Testing

This module provides functionality to enrich attack strategy results with
NIST compliance information, including control mappings, risk scoring,
documentation requirements, and traceability.
"""
from typing import Dict, List, Any
import datetime
import uuid
import copy
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
        target_behavior = attack_result.get("target_behavior", strategy_name.lower().replace("_", " "))
        response_data = attack_result.get("response", {})
        llm_response = response_data.get("response", "-") if response_data else "-"
        
        # Map severity to impact and likelihood
        impact_likelihood = self._mapper.map_severity_to_impact_likelihood(severity)
        
        # Calculate risk score
        risk_score = self._mapper.calculate_risk_score(
            impact_likelihood["likelihood"],
            impact_likelihood["impact"]
        )
   
        # Prepare documentation requirements for each test
        attack_doc_fields = {
            "test_id": uuid.uuid4().hex,
            "test_objective": target_behavior,
            "test_method": strategy_name.lower().replace("_", " "),
            "expected_results": "safe behavior from model",
            "actual_results": llm_response,
            "test_status": "pass" if attack_result.get("evaluation", {}).get("passed", False) else "fail",
            "assessment_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "assessor": "CompliantLLM-Agent",
            # supplemental fields
            "test_steps": [],
            "assessment_methods": mutation_technique,
            "assessment_objects": [],
            "risk_score": risk_score,
            "security_baseline": {}
        }

        remediation_doc_fields = {
            # Required fields
            "finding_id": uuid.uuid4().hex,
            "vulnerability": strategy_name.lower().replace("_", " "),
            "remediation_action": f"Fix {strategy_name} issues in system",
            "responsible_party": "",
            "remediation_status": "Not Started",
            "remediation_priority": "Medium",
            "estimated_completion": "",
            
            # Supplemental fields
            "remediation_approach": "",
            "compensating_controls": "",
            "remediation_resources": "",
            "verification_method": "",
            "residual_risk": ""
        }

        
        # Find a matching attack category if target behavior is specified
        attack_category = self._mapper.find_matching_attack_category(strategy_name, mutation_technique)

        # Extract relevant controls based on attack category if available
        all_tested_controls = attack_category.get("all_tested_controls", [])
        
        # create a deep copy of attack_category
        attack_category_copy = copy.deepcopy(attack_category)
        # remove all_tested_controls from attack_category_copy
        attack_category_copy.pop("all_tested_controls", None)
        
        # Build compliance data
        compliance_data = {
            "risk_score": risk_score,
            "all_tests": attack_category_copy,
            "tested_controls": all_tested_controls,
            "tested_control_ids": attack_category.get("tested_control_ids", ""),
            "framework_versions": self._mapper.get_framework_versions(),
            "passed_status": attack_result.get("evaluation", {}).get("passed", False),
            "documentation_requirements": {
                "attack": attack_doc_fields,
                "remediation": remediation_doc_fields
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


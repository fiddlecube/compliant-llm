"""Compliance Orchestrator Module

This module provides functionality to orchestrate compliance reporting across
multiple regulatory frameworks. It manages compliance adapters and coordinates
the transformation of attack strategy results into compliance reports.
"""
from typing import Dict, List, Any, Optional
import importlib
from .nist.adapter import NISTComplianceAdapter
from .gdpr.adapter import GDPRComplianceAdapter


COMPLIANCE_ADAPTERS = {
    "nist": NISTComplianceAdapter,
    "gdpr": GDPRComplianceAdapter,
}
class ComplianceOrchestrator:
    """Orchestrates compliance adapters for multiple regulatory frameworks.

    This class manages multiple compliance adapters and handles the coordination
    of transforming attack strategy results into compliance reports for various
    regulatory frameworks.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the compliance orchestrator with a configuration.

        Args:
            config: Configuration dictionary containing framework specifications
        """
        self.config = config
        self.adapters = self._initialize_adapters()

    def _initialize_adapters(self) -> Dict[str, Any]:
        """Initialize compliance adapters based on the configuration.

        Returns:
            Dictionary mapping framework names to adapter instances
        """
        adapters = {}
        for framework, adapter_class in COMPLIANCE_ADAPTERS.items():
            adapters[framework] = adapter_class()
        return adapters

    def enrich_attack_result(
        self, attack_result: Dict[str, Any], framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enrich an attack result with compliance information.

        Args:
            attack_result: The attack result to enrich
            framework: Optional framework name to use for enrichment

        Returns:
            Enriched attack result with compliance information
        """
        enriched_result = attack_result.copy()
        if framework and framework in self.adapters:
            enriched_result = self.adapters[framework].enrich_attack_result(
                enriched_result
            )
        elif not framework:
            for adapter_name, adapter in self.adapters.items():
                enriched_result = adapter.enrich_attack_result(enriched_result)

            # Extract the compliance data and add it under a framework-specific key
            if 'compliance' not in enriched_result:
                enriched_result['compliance'] = {}
                
            # Get the specific compliance data and add it under the framework namespace
            framework_compliance = enriched_result.get(f'{framework}_compliance', {})
            if framework_compliance:
                enriched_result['compliance'][framework] = framework_compliance
        
        return enriched_result
    
    def generate_compliance_reports(self, attack_results: List[Dict[str, Any]], framework: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Generate comprehensive compliance reports from attack results.
        
        Args:
            attack_results: List of attack results from various strategies
            
        Returns:
            Dict mapping framework names to compliance reports
        """
        reports = {}

        if framework and framework in self.adapters:
            reports[framework] = self.adapters[framework].generate_compliance_report(attack_results)
        elif not framework:
            for framework_name, adapter in self.adapters.items():
                reports[framework_name] = adapter.generate_compliance_report(attack_results)
            
        return reports
    
    def generate_consolidated_report(self, attack_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a consolidated report including compliance data from all frameworks.
        
        Args:
            attack_results: List of attack results from various strategies
            
        Returns:
            Consolidated report with sections for each compliance framework
        """
        # Generate individual framework reports
        framework_reports = self.generate_compliance_reports(attack_results)
        
        # Create a consolidated report structure
        consolidated_report = {
            "compliance_summary": {
                "frameworks_applied": list(framework_reports.keys()),
                "framework_count": len(framework_reports),
                "framework_reports": framework_reports
            }
        }
        
        return consolidated_report

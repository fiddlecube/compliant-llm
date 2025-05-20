"""
Base Compliance Adapter

This module defines the base abstract class for all compliance adapters.
These adapters transform attack strategy results into compliance reports
for various regulatory frameworks.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import yaml
from pathlib import Path
import os


class BaseComplianceAdapter(ABC):
    """Base class for compliance adapters.

    This abstract class defines the interface that all compliance adapters must
    implement. Adapters are responsible for enriching attack results with
    compliance-specific information and generating compliance reports.
    """

    @abstractmethod
    def enrich_attack_result(self, attack_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich an attack result with compliance-specific information.

        Args:
            attack_result: A dictionary containing the result of an attack strategy.

        Returns:
            The enriched attack result with compliance information added.
        """
        pass

    @abstractmethod
    def generate_compliance_report(
        self, attack_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a compliance report based on a list of attack results.

        Args:
            attack_results: A list of dictionaries containing the results
                           of attack strategies.

        Returns:
            A compliance report as a dictionary.
        """
        pass

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from the adapter's directory.

        Args:
            filename: The name of the YAML file to load.

        Returns:
            The parsed YAML content as a dictionary.
        """
        filepath = self._base_path / filename
        with open(filepath, "r") as file:
            return yaml.safe_load(file)

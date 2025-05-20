"""
NIST Compliance Mapping Loaders

Handles loading and validating YAML configuration files for NIST compliance mappings.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class NISTComplianceLoader:
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the NIST compliance loader.
        
        Args:
            base_path: Optional path to YAML files. If None, uses the default path.
        """
        self._base_path = base_path or Path(os.path.dirname(os.path.abspath(__file__)))
        
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from the NIST mappings directory.
        
        Args:
            filename: Name of YAML file to load
            
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
            
    def load_all_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load all required YAML mappings for NIST compliance.
        
        Returns:
            Dict containing all loaded mapping files
        """
        return {
            "strategy_mappings": self.load_yaml("mappings/strategy_mapping.yaml"),
            "risk_scoring": self.load_yaml("mappings/risk_scoring.yaml"),
            "doc_requirements": self.load_yaml("mappings/documentation_requirements.yaml"),
            "controls_reference": self.load_yaml("mappings/controls_reference.yaml")
        }
        
    def validate_mappings(self, mappings: Dict[str, Dict[str, Any]]) -> bool:
        """Validate that all required mappings are present and well-formed.
        
        Args:
            mappings: Dict of loaded mappings
            
        Returns:
            True if all mappings are valid, False otherwise
        """
        required_keys = ["strategy_mappings", "risk_scoring", "doc_requirements", "controls_reference"]
        
        # Check that all required mappings are present
        for key in required_keys:
            if key not in mappings or not mappings[key]:
                print(f"Missing or empty required mapping: {key}")
                return False
                
        # Validate structure of strategy mappings
        strategy_mappings = mappings.get("strategy_mappings", {})
        if "strategy_mappings" not in strategy_mappings:
            print("Invalid strategy mappings format: missing 'strategy_mappings' key")
            return False
            
        # Validate structure of risk scoring
        risk_scoring = mappings.get("risk_scoring", {})
        if "risk_scoring" not in risk_scoring:
            print("Invalid risk scoring format: missing 'risk_scoring' key")
            return False
            
        # More detailed validation could be added here
        
        return True

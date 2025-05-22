"""
UI-specific configuration adapter for Compliant LLM.
"""
import os
from typing import Dict, List, Any, Optional
from .config import ConfigManager
from core.runner import execute_prompt_tests_with_orchestrator

class UIConfigAdapter:
    """Adapter for handling UI-specific configurations and test execution."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the UI config adapter.
        
        Args:
            config_manager: Optional ConfigManager instance to use
        """
        self.config_manager = config_manager or ConfigManager()
        self.default_config = {
            "provider_name": "openai",  # Default provider
            "model": "gpt-4o",          # Default model
            "temperature": 0.7,        # Default temperature
            "max_tokens": 2000,        # Default max tokens
            "timeout": 30,             # Default timeout in seconds
            "prompt": {"content": "You are a helpful assistant"},  # Default prompt
            "strategies": [],  # Default strategies
        }
    
    def run_test(self, prompt: str, strategies: List[str]) -> Dict[str, Any]:
        """
        Run tests with UI-specific configuration.
        
        Args:
            prompt: The system prompt to test
            strategies: List of test strategies to use
            
        Returns:
            Dictionary containing test results
            
        Raises:
            ValueError: If required parameters are missing
        """
        if not prompt:
            raise ValueError("Prompt is required")
        if not strategies:
            raise ValueError("At least one strategy is required")
            
        # Create test configuration
        test_config = {
            "prompt": {"content": prompt},
            "strategies": strategies,
            "provider": {
                "name": self.default_config["provider_name"],
                "api_key": os.getenv(f"{self.default_config['provider_name'].upper()}_API_KEY", '')
            },
            "model": self.default_config["model"],
            "temperature": self.default_config["temperature"],
            "timeout": self.default_config["timeout"],
            "max_tokens": self.default_config["max_tokens"]
        }
        
        # Execute the test with orchestrator
        return execute_prompt_tests_with_orchestrator(test_config)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the default configuration.
        
        Args:
            config: Dictionary containing configuration updates
        """
        # Handle provider name specially since it's nested in the config
        if "provider" in config:
            self.default_config["provider_name"] = config["provider"]
        else:
            self.default_config.update(config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        config = self.default_config.copy()
        # Convert provider_name back to provider for backward compatibility
        config["provider"] = config.pop("provider_name", "openai")
        return config

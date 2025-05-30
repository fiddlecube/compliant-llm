# flake8: noqa E501
"""
CLI adapter for configuration management.

This module provides an adapter between the CLI layer and the config manager.
It converts CLI arguments to a format that can be processed by the ConfigManager.
"""

import os
from typing import Dict, Any, Optional

from .config import ConfigManager, find_config_file, DEFAULT_REPORTS_DIR


class CLIConfigAdapter:
    """
    Adapter for CLI configuration handling.
    
    This class provides methods to convert CLI arguments to a configuration
    dictionary that can be used by the ConfigManager.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the adapter."""
        self.config_manager = config_manager or ConfigManager()
    
    def load_from_cli(self, 
                    config_path: Optional[str] = None,
                    prompt: Optional[str] = None,
                    strategy: Optional[str] = None,
                    provider: Optional[str] = None,
                    output: Optional[str] = None,
                    parallel: Optional[bool] = None,
                    timeout: Optional[int] = None,
                    **kwargs):
        """
        Load configuration from CLI arguments.
        
        Args:
            config: Path to configuration file
            prompt: System prompt to test
            strategy: Test strategy to use (comma-separated for multiple)
            provider: LLM provider name
            output: Output file path for results
            parallel: Whether to run tests in parallel
            timeout: Timeout in seconds for LLM requests
            **kwargs: Additional keyword arguments
            
        Returns:
            Processed configuration dictionary
        """
        # Initialize a ConfigManager instance
        self.config_manager = self.config_manager or ConfigManager()
        config_dict = {}
        
        # Load from config file if specified
        if config_path:
            config = find_config_file(config_path)
            if not config:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            # Load the configuration
            self.config_manager = ConfigManager(config)
            
            # Store original config for CLI overrides
            config_dict = self.config_manager.config.copy() if self.config_manager.config else {}
        else:
            # Create an empty config manager
            self.config_manager = ConfigManager()
            config_dict = {}
        
        
        # Apply CLI overrides to the config dictionary
        if prompt:
            if 'prompt' not in config_dict:
                config_dict['prompt'] = {}
            if isinstance(config_dict.get('prompt'), dict):
                config_dict['prompt']['content'] = prompt
            else:
                config_dict['prompt'] = prompt
        
        strategy_list = []
        if strategy:
            # Parse comma-separated strategy string
            strategy_list = [s.strip() for s in strategy.split(',') if s.strip()]
            
            if strategy_list:
                config_dict['strategies'] = strategy_list
        
        if provider:
            if 'provider' not in config_dict:
                config_dict['provider'] = {}
            if isinstance(config_dict.get('provider'), dict):
                config_dict['provider']['name'] = provider
                config_dict['provider']['provider_name'] = provider
                config_dict['provider']['model'] = provider
            else:
                config_dict['provider'] = provider
                
        # Set output path
        config_dict['output'] = {"path": str(DEFAULT_REPORTS_DIR), "filename": output or "report"}
            
        # Set timeout if provided
        if timeout:
            if 'provider' not in config_dict:
                config_dict['provider'] = {}
            if isinstance(config_dict.get('provider'), dict):
                config_dict['provider']['timeout'] = timeout
                
        # Set parallel option if provided
        if parallel is not None:
            if 'features' not in config_dict:
                config_dict['features'] = {}
            config_dict['features']['parallel_testing'] = parallel
        # Update the config manager with our modified config
        self.config_manager.config = config_dict
    
    def get_runner_config(self) -> Dict[str, Any]:
        """
        Get the runner configuration from the config manager.
        
        Returns:
            Runner configuration dictionary
        
        Raises:
            ValueError: If config_manager has not been initialized
        """
        if not self.config_manager:
            raise ValueError("Config manager not initialized. Call load_from_cli first.")
        
        return self.config_manager.get_runner_config()
    
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if the configuration is valid, False otherwise
        """
        if not self.config_manager:
            return False
        
        try:
            # Try to get the runner config, which validates the configuration
            self.config_manager.get_runner_config()
            return True
        except Exception:
            return False
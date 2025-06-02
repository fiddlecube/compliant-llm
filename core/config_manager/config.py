"""
Configuration management for Compliant LLM.

This module handles configuration loading, validation, and template processing.
"""
import os
import copy
import yaml
import jinja2
from typing import Dict, List, Any, Optional

from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, get_key

DEFAULT_REPORTS_DIR = Path.home() / '.compliant-llm' / 'reports'

load_dotenv()
class ConfigManager:
    """Manages configuration for Compliant LLM."""

    def __init__(self, config_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the config manager.
        Args:
            config_path: Optional path to a config file to load
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.processed_config: Dict[str, Any] = {}

        # If config path provided, load it
        if config_path:
            self.load_config(config_path)
        
        if config:
            self.config = config

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load a configuration file.

        Args:
            config_path: Path to the config file
            
        Returns:
            The loaded configuration
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the config file is invalid YAML
        """
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.config_path = config_path
            return self.config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing config file: {e}")
    
    def process_template_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """
        Process Jinja2 template variables in the content.
        
        Args:
            content: The content with template variables
            variables: The variables to use for rendering
            
        Returns:
            The rendered content
        """
        # Create Jinja2 environment
        env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Render the template
        template = env.from_string(content)
        return template.render(**variables)
    
    def load_prompt_from_template(self, prompt_config: Dict[str, Any]):
        """
        Load a prompt from a predefined template library.
        
        Args:
            prompt_config: The prompt configuration dictionary
            
        Returns:
            The prompt content from the template
            
        Raises:
            ValueError: If the template name is not specified or not found
        """
        pass

    def load_prompt_from_third_party(self, prompt_config: Dict[str, Any]):
        """
        Load a prompt from a third-party prompt repository.

        Args:
            prompt_config: The prompt configuration dictionary

        Returns:
            The prompt content

        Raises:
            ValueError: If the source is not supported or the required parameters are missing
        """
        pass

    def get_prompt_content(self) -> str:
        """
        Get the prompt content from the configuration.

        Returns:
            The prompt content as a string.

        Raises:
            ValueError: If the prompt is not found or cannot be loaded
        """
        if not self.config:
            raise ValueError("No configuration loaded")

        if "prompt" not in self.config:
            raise ValueError("Prompt configuration not found")

        prompt_config = self.config["prompt"]

        # Handle different prompt sources
        if "content" in prompt_config:
            # Direct content
            return prompt_config["content"]
        elif "file" in prompt_config:
            # Load from file
            file_path = prompt_config["file"]
            if not os.path.exists(file_path):
                raise ValueError(f"Prompt file not found: {file_path}")

            with open(file_path, "r") as f:
                return f.read()
        elif "source" in prompt_config:
            # Load from third-party source
            # return self.load_prompt_from_third_party(prompt_config)
            return ""
        elif "template_name" in prompt_config:
            # Load from template library
            # return self.load_prompt_from_template(prompt_config)
            return ""
        else:
            raise ValueError("Unrecognized prompt configuration format")

    def get_prompt(self) -> str:
        """
        Get the processed prompt from the configuration.
        
        Returns:
            The processed prompt content
        """
        if not self.config:
            raise ValueError("No configuration loaded")

        prompt_content = ""

        # Extract prompt content
        if 'prompt' in self.config:
            if isinstance(self.config['prompt'], dict):
                prompt_config = self.config['prompt']

                # Option 1: Direct content specification
                if 'content' in prompt_config:
                    prompt_content = prompt_config['content']
                # Option 2: Load from file
                elif 'file' in prompt_config:
                    # Load from file
                    prompt_file = prompt_config['file']
                    prompt_path = os.path.abspath(prompt_file)
                    if not os.path.exists(prompt_path):
                        # Try relative to config file
                        config_dir = os.path.dirname(self.config_path) if self.config_path else os.getcwd()
                        prompt_path = os.path.join(config_dir, prompt_file)
                    
                    if os.path.exists(prompt_path):
                        with open(prompt_path, 'r') as f:
                            prompt_content = f.read()
                    else:
                        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
                
                # Option 3: Load from a third-party service
                elif 'source' in prompt_config:
                    prompt_content = self.load_prompt_from_third_party(prompt_config)
                
                # Option 4: Use a predefined template
                elif 'template' in prompt_config:
                    # Convert to the format expected by load_prompt_from_third_party
                    template_config = {
                        'source': 'template',
                        'template_name': prompt_config['template']
                    }
                    prompt_content = self.load_prompt_from_third_party(template_config)
                
            else:
                # Old format with direct prompt string
                prompt_content = self.config['prompt']
        
        # Process template variables if present
        if prompt_content and isinstance(self.config['prompt'], dict) and 'variables' in self.config['prompt']:
            prompt_content = self.process_template_variables(
                prompt_content, 
                self.config['prompt']['variables']
            )
        
        return prompt_content
    
    def process_config(self) -> Dict[str, Any]:
        """Process the loaded configuration."""
        if not self.config:
            raise ValueError("No configuration loaded")
            
        processed_config = copy.deepcopy(self.config)
        
        # Process prompt if present
        if "prompt" in processed_config:
            prompt_config = processed_config["prompt"]
            
            # Handle different prompt sources
            if "content" in prompt_config:
                # Direct content - nothing to process
                pass
            elif "file" in prompt_config:
                # Load from file
                file_path = prompt_config["file"]
                if not os.path.exists(file_path):
                    raise ValueError(f"Prompt file not found: {file_path}")
                    
                with open(file_path, "r") as f:
                    prompt_config["content"] = f.read()
                del prompt_config["file"]
            elif "source" in prompt_config:
                # Load from third-party source
                prompt_content = self.load_prompt_from_third_party(prompt_config)
                # Replace with direct content
                prompt_config.clear()
                prompt_config["content"] = prompt_content
                
        self.processed_config = processed_config
        return processed_config
    
    def get_strategies(self) -> List[str]:
        """
        Get the list of enabled test strategies.
        
        Returns:
            List of strategy names
        """
        if not self.config:
            return ['prompt_injection']  # Default
        
        strategies = []
        
        # Modern format with strategy objects
        if 'strategies' in self.config:
            for strategy in self.config['strategies']:
                if isinstance(strategy, dict):
                    if strategy.get('enabled', True):
                        strategies.append(strategy['name'])
                elif isinstance(strategy, str):
                    strategies.append(strategy)
        # Legacy format with comma-separated string
        elif 'strategy' in self.config:
            if isinstance(self.config['strategy'], str):
                strategies = [s.strip() for s in self.config['strategy'].split(',')]
        
        return strategies or ['prompt_injection']  # Default to prompt_injection if empty
    
    def get_provider(self) -> str:
        """
        Get the provider name from the configuration.
        
        Returns:
            Provider name string
        """
        if not self.config:
            return ''  # Default
        
        # Modern format with provider object
        if 'provider' in self.config:
            if isinstance(self.config['provider'], dict):
                return self.config['provider'].get('provider_name') or self.config['provider'].get('model', '')  # noqa: E501
            return self.config['provider']
        # Legacy format
        elif 'provider_name' in self.config:
            return self.config['provider_name']
        
        return ''  # Default

    def get_output_path(self) -> Dict[str, str]:
        """
        Get the output path for reports.
        
        Returns:
            Output file path
        """

        if not self.config:
            return {'path': str(DEFAULT_REPORTS_DIR), 'filename': 'report'}  # Default
        
        # Extract output path
        if 'output' in self.config:
            output_config = self.config['output']
            path = output_config.get('path', './')
            filename = output_config.get('filename', 'report')
            
            # Ensure path exists
            os.makedirs(path, exist_ok=True)
            
            return {'path': path, 'filename': filename}
        
        return {'path': str(DEFAULT_REPORTS_DIR), 'filename': 'report'}  # Default
    
    def get_runner_config(self) -> Dict[str, Any]:
        """
        Get the configuration in a format compatible with the runner.
        
        Returns:
            Dictionary with runner-compatible configuration
        """
        if not self.config:
            raise ValueError("No configuration loaded")
        
        prompt = self.get_prompt()
        strategies = self.get_strategies()
        provider = self.get_provider()
        # Format for the runner
        api_key_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_key, 'n/a') or get_key(".env", api_key_key)
        runner_config = {
            'prompt': prompt,
            'strategies': strategies,
            'provider_name': provider,
            'provider': {
                'provider_name': provider,
                'model': provider,
                'api_key': api_key,
            }
        }
        
        # Advanced options - check if parallel testing is enabled
        if 'features' in self.config and isinstance(self.config['features'], dict):
            features = self.config['features']
            if features.get('parallel_testing', False):
                runner_config['parallel'] = True
                runner_config['max_threads'] = features.get('max_threads', 4)
        
        # Provider options
        if 'provider' in self.config and isinstance(self.config['provider'], dict):
            provider_config = self.config['provider']
            if 'timeout' in provider_config:
                runner_config['timeout'] = provider_config['timeout']
            if 'max_retries' in provider_config:
                runner_config['max_retries'] = provider_config['max_retries']
            if 'temperature' in provider_config:
                runner_config['temperature'] = provider_config['temperature']
            if 'fallbacks' in provider_config:
                runner_config['fallbacks'] = provider_config['fallbacks']
        # Output options
        runner_config['output_path'] = self.get_output_path()
        return runner_config


def find_config_file(config_name: Optional[str]) -> Optional[str]:
    """
    Find a config file by name, looking in various locations.
    
    Args:
        config_name: Name of the config file. If None, will search in default locations.
        
    Returns:
        Full path to the config file, or None if not found
    """
    # If no name specified, use default
    if not config_name:
        config_name = "config.yaml"
            
    # If specific path provided, just return it if exists
    if os.path.isabs(config_name) or os.path.exists(config_name):
        if os.path.isfile(config_name):
            return config_name
        return None
            
    # Otherwise, look in standard locations
    search_paths = [
        os.getcwd(),  # Current directory
        os.path.join(os.getcwd(), "configs"),  # configs/ subdirectory
    ]
    
    # Search all paths
    for path in search_paths:
        full_path = os.path.join(path, config_name)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return full_path
            
    # Not found
    return None


def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """
    Load and validate a configuration file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Validated configuration dictionary ready for the runner
        
    Raises:
        ValueError: If the config is invalid
    """
    # Find config file if needed
    full_path = find_config_file(config_path)
    if not full_path:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Create manager and load config
    config_manager = ConfigManager(full_path)
    
    # Get runner config
    try:
        runner_config = config_manager.get_runner_config()
        return runner_config
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")

"""
UI-specific configuration adapter for Compliant LLM.
"""
import os
from dotenv import load_dotenv, get_key
from typing import Dict, List, Any, Optional
from .config import ConfigManager, DEFAULT_REPORTS_DIR
from core.runner import execute_prompt_tests_with_orchestrator
from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
)

load_dotenv()
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
            "temperature": 0.7,        # Default temperature
            "max_tokens": 2000,        # Default max tokens
            "timeout": 30,             # Default timeout in seconds
            "output_path": {"path": str(DEFAULT_REPORTS_DIR), "filename": "report"},  # Default output path
        }
    
    def run_test(self, prompt: str, strategies: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
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
        api_key_key = f"{config['provider_name'].upper()}_API_KEY"
        api_key = os.getenv(api_key_key, 'n/a') or get_key(".env", api_key_key)

        test_config = {
            "prompt": {"content": prompt},
            "strategies": strategies,
            "provider": {
                "provider_name": f"{config['provider_name']}/{config['model']}",
                "model": f"{config['provider_name']}/{config['model']}",
                "api_key": api_key,
            },
            "temperature": self.default_config["temperature"],
            "timeout": self.default_config["timeout"],
            "max_tokens": self.default_config["max_tokens"],
            "output_path": self.default_config["output_path"]
        }
        console = Console()
        console.print(f"[bold cyan]Running test with config: {test_config}[/]")
        

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Testing prompt security", total=None)
            report_data = execute_prompt_tests_with_orchestrator(test_config)
            progress.update(task, completed=True)
        
        console.print("[bold green]Tests completed successfully![/]")
        console.print(f"[bold cyan]Report saved successfully at {report_data['report_metadata']['path']}[/]")
        console.print("\n")
        
        # Execute the test with orchestrator
        return report_data
    
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
        config["model"] = config.pop("model_name", "gpt-4o")
        return config

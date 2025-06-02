"""
UI-specific configuration adapter for Compliant LLM.
"""
import os
from dotenv import load_dotenv, get_key
from typing import Dict, List, Any, Optional
from .config import ConfigManager, DEFAULT_REPORTS_DIR
from core.runner import execute_prompt_tests_with_orchestrator
from core.data_store import model_config_store
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
    
    def run_test(self, config_id: str, prompt_override: Optional[str] = None, strategies_override: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run tests using a stored configuration profile, with optional overrides.

        Args:
            config_id: The ID of the configuration profile to use.
            prompt_override: Optional new prompt content to use for this run.
            strategies_override: Optional new list of strategies to use for this run.

        Returns:
            Dictionary containing test results.

        Raises:
            ValueError: If the configuration profile is not found or required parameters are missing.
        """
        full_runner_config = self.get_profile(config_id)
        if not full_runner_config:
            raise ValueError(f"Configuration profile with ID '{config_id}' not found.")

        # Make a copy to avoid modifying the stored config directly with temporary overrides
        test_run_config = full_runner_config.copy()

        # Apply overrides if any
        if prompt_override is not None:
            # Assuming prompt is stored as {'content': '...'}
            if 'prompt' not in test_run_config or not isinstance(test_run_config.get('prompt'), dict):
                 test_run_config['prompt'] = {}
            test_run_config['prompt']['content'] = prompt_override 

        if strategies_override is not None:
            test_run_config['strategies'] = strategies_override
        
        test_run_config['output_path'] = test_run_config.get('output_path', self.default_config['output_path']) # if not specified in config, use default

        # Ensure essential keys are present (they should be from the stored config)
        if 'prompt' not in test_run_config or (isinstance(test_run_config.get('prompt'), dict) and 'content' not in test_run_config.get('prompt', {})):
             if prompt_override is None: # only raise if no override was given
                raise ValueError("Prompt content is missing in the configuration and no override provided.")
        if 'strategies' not in test_run_config or not test_run_config['strategies']:
            if strategies_override is None: # only raise if no override was given
                raise ValueError("Strategies are missing in the configuration and no override provided.")
        if 'provider_name' not in test_run_config or 'model' not in test_run_config:
            raise ValueError("Provider information (provider_name, model) is missing in the configuration.")

        console = Console()
        console.print(f"[bold cyan]Running test with profile ID '{config_id}':[/]")
        console.print(f"[bold cyan]Effective config for run: {test_run_config}[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Testing prompt security", total=None)
            # Pass the fully prepared test_run_config
            report_data = execute_prompt_tests_with_orchestrator(test_run_config) 
            progress.update(task, completed=True)
        
        console.print("[bold green]Tests completed successfully![/]")
        report_file_path = report_data.get('report_metadata', {}).get('path')
        if report_file_path:
            console.print(f"[bold cyan]Report saved successfully at {report_file_path}[/]")
            # Add report to config's past_runs
            model_config_store.add_report_to_config(config_id, str(report_file_path))
        else:
            console.print("[bold yellow]Report path not found in report data. Cannot link to profile.[/]")
        console.print("\n")
        
        return report_data

    # --- Profile Management Methods ---

    def upsert_profile(self, runner_config_data: Dict[str, Any], profile_name: Optional[str] = None) -> str:
        """Saves a new profile or updates an existing one based on the presence of 'id' in runner_config_data.
        Returns the ID of the saved/updated configuration.
        """
        # model_config_store.save_config ensures 'id' is present and handles profile_name
        model_config_store.save_config(runner_config_data, profile_name=profile_name)
        return runner_config_data['id'] # 'id' is guaranteed by save_config

    def get_profile(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific configuration profile by its ID."""
        return model_config_store.get_config(config_id)

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Lists all saved configuration profiles."""
        return model_config_store.list_configs()

    def delete_profile(self, config_id: str) -> bool:
        """Deletes a configuration profile by its ID. Returns True if deleted."""
        return model_config_store.delete_config(config_id)
    
    # --- Existing Methods for Default/Unsaved Config --- 

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

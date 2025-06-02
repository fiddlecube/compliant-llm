# flake8: noqa E501
import os
import asyncio
from datetime import datetime
from typing import Dict, Any
from rich.console import Console

# Add these imports at the top of the file
from core.strategies.base import BaseAttackStrategy
from core.test_engine.orchestrator import AttackOrchestrator

# Porting out strategies
from core.strategies.attack_strategies.prompt_injection.base import PromptInjectionStrategy
from core.strategies.attack_strategies.jailbreak.base import JailbreakStrategy


from core.strategies.attack_strategies.owasp_strategy import OWASPPromptSecurityStrategy
from core.providers.litellm_provider import LiteLLMProvider


from core.config_manager.cli_adapter import CLIConfigAdapter
from core.reporter import save_report

def execute_prompt_tests_with_orchestrator(config_dict):
    """
    Execute prompt tests using the test engine and orchestrator.
    
    Args:
        config_dict: Configuration dictionary containing all necessary parameters
            for running tests. This should be a fully processed configuration that has
            already gone through the ConfigManager.
    
    Returns:
        Dictionary containing test results
    """
    
    start_time = datetime.now()
    # Use the provided configuration directly
    config = config_dict
    # Extract provider configuration with sensible defaults
    # model_name = config.get('provider_name') or config.get('provider', {}).get('name')
    provider_name = config.get('provider_name')
    model_name = config.get('model')
    # Get API key
    api_key = config.get('api_key')
    
    # Create provider configuration in one step
    provider_config = {
        # litellm accepts 'provider_name/model_name' as the provider
        'provider_name': f"{provider_name}/{model_name}",
        'api_key': api_key,
        'temperature': config.get('temperature', 0.7),
        'timeout': config.get('timeout', 30)
    }
    
    # Create provider
    provider = LiteLLMProvider()

    # Extract system prompt, handling both dict and string formats with default
    prompt_value = config.get('prompt', {})
    system_prompt = (prompt_value.get('content') if isinstance(prompt_value, dict) else prompt_value) or "You are a helpful assistant"
    
    # Determine strategies
    strategies = []
    
    # Check for the strategies field (supports both plural and singular forms)
    # strategies_list = config.get('strategies', config.get('strategy', []))

    
    strategies = AttackOrchestrator._create_strategies_from_config(config)

    # Create orchestrator
    orchestrator = AttackOrchestrator(
        strategies=strategies,
        provider=provider,
        config={
            **config,
            'provider_config': provider_config
        }
    )

    # try running an attack with orchestrator
    asyncio.run(orchestrator.orchestrate_attack(system_prompt, strategies))
    
    # calculate elapsed time
    elapsed_time = datetime.now() - start_time
    report_data = {}
    orchestrator_summary = orchestrator.get_attack_orchestration_summary()
    report_data['metadata'] = orchestrator_summary['metadata']
    report_data['metadata']['elapsed_seconds'] = elapsed_time.total_seconds()
    report_data['strategy_summaries'] = orchestrator_summary['strategy_summaries']
    report_data['testcases'] = orchestrator_summary['testcases']
    # Remove provider field from config before adding to report
    config_for_report = config_dict.copy()
    config_for_report.pop('provider', None)  # Remove provider if it exists
    report_data['config'] = config_for_report  # Add config dictionary to report
    
    # Add compliance report if available
    if 'compliance_report' in orchestrator_summary:
        report_data['compliance_report'] = orchestrator_summary['compliance_report']
    
    
    # Save report (optional)
    output = config_dict.get('output_path')  # Get from CLI argument
    save_report(report_data, output_path=output)
    return report_data


def execute_prompt_tests(config_path=None, config_dict=None):
    """
    Wrapper around execute_prompt_tests_with_orchestrator to maintain backward compatibility.
    
    Args:
        config_path: Path to a configuration file
        config_dict: Configuration dictionary (takes precedence over config_path)
        
    Returns:
        Dictionary containing test results
    """
    # If config_dict is provided, use it directly (CLI has already processed it)
    
    if config_dict:
        return execute_prompt_tests_with_orchestrator(config_dict=config_dict)
    
    # If config_path is provided, load it through the CLI adapter
    if config_path:
        try:
            # Use the CLIConfigAdapter to load and process the config
            cli_adapter = CLIConfigAdapter()
            cli_adapter.load_from_cli(config=config_path)
            runner_config = cli_adapter.get_runner_config()
            return execute_prompt_tests_with_orchestrator(config_dict=runner_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    # No configuration provided
    raise ValueError("No configuration provided. Please provide either config_path or config_dict.")


def execute_rerun_test(config_dict, report_file):
    start_time = datetime.now()
    # Use the provided configuration directly
    config = config_dict
    
    # Extract provider configuration with sensible defaults
    model_name = config.get('provider_name') or config.get('provider', {}).get('model')
    # Get API key with fallback to environment variable
    api_key = config.get('provider', {}).get('api_key') or os.getenv(model_name.split('/')[0].upper() + "_API_KEY", '')
    
    # Create provider configuration in one step
    provider_config = {
        'provider_name': model_name,
        'api_key': api_key,
        'temperature': config.get('temperature', 0.7),
        'timeout': config.get('timeout', 30)
    }
        
    # Create provider
    provider = LiteLLMProvider()

    # Create orchestrator
    orchestrator = AttackOrchestrator(
        strategies=[],
        provider=provider,
        config={
            **config,
            'provider_config': provider_config
        }
    )

    # try running an attack with orchestrator
    report_data = asyncio.run(orchestrator.rerun_attack(config_dict, report_file))
    
    # calculate elapsed time
    elapsed_time = datetime.now() - start_time
    report_data['metadata']['elapsed_seconds'] = elapsed_time.total_seconds()

    # Save report (optional)
    output = config_dict.get('output_path')  # Get from CLI argument
    
    if len(report_data["results"]) > 0:    
        save_report(report_data, output_path=output)
    return report_data


# flake8: noqa E501
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add these imports at the top of the file
from core.strategies.base import BaseAttackStrategy
from core.test_engine.orchestrator import AttackOrchestrator

# Attack Strategies
from core.strategies.attack_strategies.strategy import (
    # JailbreakStrategy, 
    # PromptInjectionStrategy,
    ContextManipulationStrategy,
    InformationExtractionStrategy,
    StressTesterStrategy,
    BoundaryTestingStrategy,
    SystemPromptExtractionStrategy,
)
# Porting out strategies
from core.strategies.attack_strategies.prompt_injection.base import PromptInjectionStrategy
from core.strategies.attack_strategies.jailbreak.base import JailbreakStrategy


from core.strategies.attack_strategies.owasp_strategy import OWASPPromptSecurityStrategy
from core.providers.litellm_provider import LiteLLMProvider

## Evaluators
from core.evaluators.base import BaseEvaluator
from core.evaluators.evals.owasp_evaluator import OWASPComplianceEvaluator
from core.evaluators.evals.advanced_evaluators import (
    MultiSignalEvaluator,
    SystemPromptComplianceEvaluator,
    UserPromptContextEvaluator
)


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
    model_name = config.get('provider_name') or config.get('provider', {}).get('name', 'openai/gpt-4o')
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
    

    # Extract system prompt, handling both dict and string formats with default
    prompt_value = config.get('prompt', {})
    system_prompt = prompt_value.get('content') if isinstance(prompt_value, dict) else prompt_value
    system_prompt = system_prompt or 'You are a helpful AI assistant'
    
    # Determine strategies
    strategies = []
    
    # Check for the strategies field (supports both plural and singular forms)
    strategies_list = config.get('strategies', config.get('strategy', []))


    if strategies_list:
        strategy_map = {
            # 'jailbreak': JailbreakStrategy,
            'prompt_injection': PromptInjectionStrategy,
            # 'context_manipulation': ContextManipulationStrategy,
            # 'information_extraction': InformationExtractionStrategy,
            # 'stress_tester': StressTesterStrategy,
            # 'boundary_testing': BoundaryTestingStrategy,
            # 'system_prompt_extraction': SystemPromptExtractionStrategy,
            # 'owasp': OWASPPromptSecurityStrategy
        }
        
        for strategy_name in strategies_list:
            strategy_class = strategy_map.get(strategy_name.lower())
            if strategy_class:
                strategies.append(strategy_class())
    

    # Default to a set of strategies if none specified
    if not strategies:
        strategies = [JailbreakStrategy(), PromptInjectionStrategy()]
    

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
    orchestrator_attack_results = asyncio.run(orchestrator.orchestrate_attack(system_prompt, strategies))
    
    # calculate elapsed time
    elapsed_time = datetime.now() - start_time
    report_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "provider": model_name,
            "strategies": [s.name for s in strategies],
            "test_count": len(orchestrator_attack_results),
            "success_count": sum(1 for r in orchestrator_attack_results if r.get('evaluation', {}).get('passed', False)),
            "failure_count": sum(1 for r in orchestrator_attack_results if not r.get('evaluation', {}).get('passed', False)),
            "elapsed_seconds": elapsed_time.total_seconds()
        },
        "tests": orchestrator_attack_results
    }
    
    # Save report (optional)
    output = config.get('output')  # Get from CLI argument
    if not output:  # If not specified, use default path
        output = 'reports/report.json'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    save_report(report_data, output)
    
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



# # CLI entry point (you can add this to a separate CLI script or keep it here)
# def main():
#     import argparse

#     parser = argparse.ArgumentParser(description="Prompt Security Test Runner")
#     parser.add_argument("--config", help="Path to configuration file")
#     parser.add_argument("--provider", help="LLM Provider name")
#     parser.add_argument("--api-key", help="API Key for the provider")
#     parser.add_argument("--system-prompt", help="Custom system prompt")
#     parser.add_argument("--strategy", default="jailbreak", 
#                         choices=['jailbreak', 'prompt_injection', 'context_manipulation', 'information_extraction'],
#                         help="Test strategy to use")

#     args = parser.parse_args()

#     # Create the CLI adapter for configuration handling
#     cli_adapter = CLIConfigAdapter()

#     try:
#         if args.config:
#             # Load from a specified config file
#             cli_adapter.load_from_cli(
#                 config=args.config,
#                 strategy=args.strategy,
#                 provider=args.provider,
#                 system_prompt=args.system_prompt
#             )
#         else:
#             # Load from CLI arguments only
#             cli_adapter.load_from_cli(
#                 prompt=args.system_prompt,
#                 strategy=args.strategy,
#                 provider=args.provider,
#                 api_key=args.api_key
#             )

#         # Get the runner config
#         runner_config = cli_adapter.get_runner_config()

#         # Execute the tests
#         results = execute_prompt_tests_with_orchestrator(config_dict=runner_config)
#     except Exception as e:
#         print(f"Error: {e}")
#         sys.exit(1)

#     # Print summary
#     print("\nTest Results Summary:")
#     print(f"Total Tests: {results['metadata']['test_count']}")
#     print(f"Successful Tests: {results['metadata']['success_count']}")
#     print(f"Failed Tests: {results['metadata']['failure_count']}")

# if __name__ == "__main__":
#     main()

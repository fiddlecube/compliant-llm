import os
import asyncio
from datetime import datetime
import json

# Add these imports at the top of the file
from core.strategies.base import BaseAttackStrategy
from core.test_engine.orchestrator import AttackOrchestrator

## Attack Strategies
from core.strategies.attack_strategies.strategy import (
    JailbreakStrategy, 
    PromptInjectionStrategy,
    ContextManipulationStrategy,
    InformationExtractionStrategy,
    StressTesterStrategy,
    BoundaryTestingStrategy,
    SystemPromptExtractionStrategy,
)
from core.strategies.attack_strategies.strategies.owasp_strategy import OWASPPromptInjectionStrategy
from core.providers.litellm_provider import LiteLLMProvider

## Evaluators
from core.evaluators.base import BaseEvaluator
from core.evaluators.evals.owasp_evaluator import OWASPComplianceEvaluator
from core.evaluators.evals.advanced_evaluators import MultiSignalEvaluator

from core.config import ConfigManager
from core.reporter import save_report
from core.config import load_and_validate_config


def _serialize_value(value):
    """
    Comprehensive serialization for different types of objects.
    
    Args:
        value: Any Python object to be serialized
    
    Returns:
        A JSON-serializable representation of the input value
    """
    # Comprehensive serialization for different types of objects
    if value is None:
        return None
    
    # Handle ModelResponse from LiteLLM
    if hasattr(value, 'response') and hasattr(value.response, 'choices'):
        return {
            'id': value.response.id,
            'created': value.response.created,
            'model': value.response.model,
            'object': value.response.object,
            'choices': [
                {
                    'finish_reason': choice.finish_reason,
                    'index': choice.index,
                    'message': {
                        'content': choice.message.content,
                        'role': choice.message.role
                    }
                } for choice in value.response.choices
            ],
            'usage': str(value.response.usage) if hasattr(value.response, 'usage') else None
        }
    
    # Handle dictionaries recursively
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    
    # Handle lists or tuples recursively
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    
    # Handle objects with to_dict method
    if hasattr(value, 'to_dict'):
        return value.to_dict()
    
    # Handle objects with dict method
    if hasattr(value, 'dict'):
        return value.dict()
    
    # Handle objects with model_dump method
    if hasattr(value, 'model_dump'):
        return value.model_dump()
    
    # Handle objects with __dict__ attribute
    if hasattr(value, '__dict__'):
        return value.__dict__
    
    # Fallback to string representation
    try:
        return str(value)
    except Exception:
        return repr(value)

def select_evaluator(strategies: list[BaseAttackStrategy]) -> BaseEvaluator:
    """
    Dynamically select the most appropriate evaluator based on strategies
    
    Args:
        strategies: List of attack strategies
    
    Returns:
        Most appropriate evaluator for the given strategies
    """
    # Strategy to Evaluator mapping
    evaluator_map = {
        'OWASPPromptInjectionStrategy': OWASPComplianceEvaluator,
    }
    
    # Priority-based evaluator selection
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        if strategy_name in evaluator_map:
            return evaluator_map[strategy_name]()
    
    # Fallback to multi-signal evaluator
    return MultiSignalEvaluator()

def execute_prompt_tests_with_orchestrator(
    strategies=None, 
    provider_name=None, 
    api_key=None, 
    system_prompt=None, 
    config_path=None, 
    config_dict=None
):
    """
    Execute prompt tests using the test engine and orchestrator.
    
    Args:
        strategies: List of strategies to use (optional)
        provider_name: LLM provider name (optional)
        api_key: API key for the provider (optional)
        system_prompt: System prompt to use (optional)
        config_path: Path to configuration file (optional)
        config_dict: Configuration dictionary (optional)
    
    Returns:
        Dictionary containing test results
    """
    # Load configuration if not provided
    if config_path:
        config = load_and_validate_config(config_path)
    elif config_dict:
        config = config_dict
    else:
        config = {}
    
    # Extract or set default values
    provider_name = provider_name or config.get('provider', {}).get('name', 'openai/gpt-4o')
    api_key = api_key or config.get('provider', {}).get('api_key', '')
    
    # Fallback to environment variable for API key
    if not api_key:
        env_var = provider_name.split('/')[0].upper() + "_API_KEY"
        api_key = os.getenv(env_var, '')
    
    # Determine system prompt
    if system_prompt is None:
        if config_path:
            config_manager = ConfigManager(config_path)
            system_prompt = config_manager.get_prompt()
        elif 'prompt' in config and isinstance(config['prompt'], dict):
            system_prompt = config['prompt'].get('content', 'You are a helpful AI assistant')
        else:
            system_prompt = 'You are a helpful AI assistant'
    
    # Determine strategies
    if strategies is None:
        # Default to Jailbreak strategy if no strategies specified
        strategies = [OWASPPromptInjectionStrategy()]
    elif isinstance(strategies, str):
        # Convert string to strategy
        strategy_map = {
            'jailbreak': JailbreakStrategy,
            'prompt_injection': PromptInjectionStrategy,
            'context_manipulation': ContextManipulationStrategy,
            'information_extraction': InformationExtractionStrategy,
            'stress_tester': StressTesterStrategy,
            'boundary_testing': BoundaryTestingStrategy,
            'system_prompt_extraction': SystemPromptExtractionStrategy,
            'owasp': OWASPPromptInjectionStrategy
        }
        strategies = [strategy_map.get(strategies.lower(), JailbreakStrategy)()]
    
    # Create provider configuration
    provider_config = {
        'model': provider_name,
        'api_key': api_key,
        'temperature': config.get('temperature', 0.7),
        'timeout': config.get('timeout', 30)
    }
    
    # Create provider
    provider = LiteLLMProvider()
    
    # Select evaluator based on strategies
    evaluator = select_evaluator(strategies)
    
    # Create orchestrator
    orchestrator = AttackOrchestrator(
        strategies=strategies,
        provider=provider,
        evaluator=evaluator,
        config={
            **config,
            'provider_config': provider_config
        }
    )
    
    # Collect attack prompts
    attack_prompts = asyncio.run(orchestrator.collect_attack_prompts())
    
    # Execute attacks
    results = []
    for attack_data in attack_prompts:
        result = asyncio.run(orchestrator.execute_single_attack(
            system_prompt=system_prompt,
            attack_data=attack_data
        ))
        results.append(result)
    
    serializable_results = []
    print("Results::", results)
    for result in results:
        serializable_result = {}
        for key, value in result.items():
            serializable_result[key] = _serialize_value(value)
        serializable_results.append(serializable_result)

    print("Serializable Results::", serializable_results)
    
    report_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "provider": provider_name,
            "strategies": [s.name for s in strategies],
            "test_count": len(serializable_results),
            "success_count": sum(1 for r in serializable_results if r.get('evaluation', {}).get('passed', False)),
            "failure_count": sum(1 for r in serializable_results if not r.get('evaluation', {}).get('passed', False))
        },
        "tests": serializable_results
    }
    
    # Save report (optional)
    output_path = config.get('output_path', 'reports/report.json')
    save_report(report_data, output_path)
    
    return report_data

# Modify existing execute_prompt_tests to use the new orchestrator method
def execute_prompt_tests(config_path=None, config_dict=None):
    """
    Wrapper around execute_prompt_tests_with_orchestrator to maintain backward compatibility.
    """
    return execute_prompt_tests_with_orchestrator(
        config_path=config_path,
        config_dict=config_dict
    )

# CLI entry point (you can add this to a separate CLI script or keep it here)
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Prompt Security Test Runner")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--provider", help="LLM Provider name")
    parser.add_argument("--api-key", help="API Key for the provider")
    parser.add_argument("--system-prompt", help="Custom system prompt")
    parser.add_argument("--strategy", default="jailbreak", 
                        choices=['jailbreak', 'prompt_injection', 'context_manipulation', 'information_extraction'],
                        help="Test strategy to use")
    
    args = parser.parse_args()
    
    # Run tests
    results = execute_prompt_tests_with_orchestrator(
        strategies=args.strategy,
        provider_name=args.provider,
        api_key=args.api_key,
        system_prompt=args.system_prompt,
        config_path=args.config
    )
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"Total Tests: {results['metadata']['test_count']}")
    print(f"Successful Tests: {results['metadata']['success_count']}")
    print(f"Failed Tests: {results['metadata']['failure_count']}")

if __name__ == "__main__":
    main()
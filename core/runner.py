import os
import asyncio
from datetime import datetime
from typing import Dict, Any

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
from core.evaluators.evals.advanced_evaluators import (
    MultiSignalEvaluator,
    SystemPromptComplianceEvaluator,
    UserPromptContextEvaluator
)

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
    Select the most appropriate evaluator based on strategies
    
    Args:
        strategies: List of attack strategies
    
    Returns:
        Composite evaluator combining specific evaluators for given strategies
    """
    # Comprehensive strategy to evaluator mapping
    strategy_evaluator_map = {
        # OWASP Strategies
        'OWASPPromptInjectionStrategy': OWASPComplianceEvaluator,
        'OWASPPromptSecurityStrategy': OWASPComplianceEvaluator,
        
        # Jailbreak and System Prompt Strategies
        'JailbreakStrategy': SystemPromptComplianceEvaluator,
        'SystemPromptExtractionStrategy': SystemPromptComplianceEvaluator,
        
        # User Context and Prompt Strategies
        'UserContextStrategy': UserPromptContextEvaluator,
        'PromptInjectionStrategy': UserPromptContextEvaluator,
        
        # Information and Context Manipulation Strategies
        'InformationExtractionStrategy': MultiSignalEvaluator,
        'ContextManipulationStrategy': MultiSignalEvaluator,
        
        # Stress and Boundary Testing Strategies
        'StressTesterStrategy': MultiSignalEvaluator,
        'BoundaryTestingStrategy': MultiSignalEvaluator
    }
    
    # Collect specific evaluators
    specific_evaluators = []
    
    # Collect evaluators based on strategies
    for strategy in strategies:
        strategy_name = strategy.__class__.__name__
        if strategy_name in strategy_evaluator_map:
            specific_evaluators.append(strategy_evaluator_map[strategy_name]())
    
    # If no specific evaluators found, use multi-signal evaluator
    if not specific_evaluators:
        return MultiSignalEvaluator()
    
    # If only one evaluator, return it
    if len(specific_evaluators) == 1:
        return specific_evaluators[0]
    
    # If multiple evaluators, create a composite evaluator
    class CompositeEvaluator(BaseEvaluator):
        def __init__(self, evaluators):
            self.evaluators = evaluators
        
        async def evaluate(self, system_prompt: str, user_prompt: str, llm_response: Dict[str, Any]) -> Dict[str, Any]:
            # Run all evaluators concurrently
            evaluation_results = await asyncio.gather(
                *[evaluator.evaluate(system_prompt, user_prompt, llm_response) 
                  for evaluator in self.evaluators]
            )
            
            # Combine results
            combined_results = {
                'passed': all(result.get('passed', False) for result in evaluation_results),
                'evaluations': evaluation_results,
                'compliance_scores': [
                    result.get('compliance_score', result.get('intent_alignment_score', 0.0)) 
                    for result in evaluation_results
                ]
            }
            
            # Calculate overall compliance score
            combined_results['overall_compliance_score'] = (
                sum(combined_results['compliance_scores']) / 
                len(combined_results['compliance_scores'])
            ) if combined_results['compliance_scores'] else 0.0
            
            return combined_results
    
    return CompositeEvaluator(specific_evaluators)

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
        strategies = [OWASPPromptInjectionStrategy(), JailbreakStrategy(), PromptInjectionStrategy(), ContextManipulationStrategy(), InformationExtractionStrategy(), StressTesterStrategy(), BoundaryTestingStrategy(), SystemPromptExtractionStrategy()]
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

    print("Evaluator::", evaluator)
    
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
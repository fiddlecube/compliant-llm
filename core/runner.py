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
    
    return CompositeEvaluator(specific_evaluators)

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

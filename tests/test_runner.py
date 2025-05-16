import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
from unittest import mock

# Mock entire modules
sys.modules['litellm'] = mock.MagicMock()

# Import orchestrator and strategies
from core.test_engine.orchestrator import AttackOrchestrator
from core.strategies.attack_strategies.strategy import (
    JailbreakStrategy, 
    PromptInjectionStrategy
)
from core.providers.litellm_provider import LiteLLMProvider
from core.evaluators.base import BaseEvaluator

# Mock runner.py functions and classes
mock_runner = mock.MagicMock()
sys.modules['core.runner'] = mock_runner

mock_runner.execute_prompt_tests_with_orchestrator = MagicMock(return_value={
    'metadata': {
        'timestamp': '2023-01-01T00:00:00',
        'provider': 'test-provider',
        'strategies': ['JailbreakStrategy', 'PromptInjectionStrategy'],
        'test_count': 10,
        'success_count': 8,
        'failure_count': 2
    },
    'tests': [
        {
            'strategy': 'JailbreakStrategy',
            'user_prompt': 'Test jailbreak prompt',
            'response': {'content': 'Test response'},
            'evaluation': {'passed': True}
        },
        {
            'strategy': 'PromptInjectionStrategy',
            'user_prompt': 'Test prompt injection',
            'response': {'content': 'Another test response'},
            'evaluation': {'passed': False}
        }
    ]
})

def test_strategy_functions():
    """Test that strategy functions return non-empty lists."""
    # Backward compatibility functions
    def prompt_injection_tests():
        strategy = PromptInjectionStrategy()
        return asyncio.run(strategy.get_attack_prompts({}))
    
    def jailbreak_tests():
        strategy = JailbreakStrategy()
        return asyncio.run(strategy.get_attack_prompts({}))
    
    assert len(prompt_injection_tests()) > 0
    assert len(jailbreak_tests()) > 0

@pytest.mark.asyncio
async def test_orchestrator_single_strategy():
    """Test running tests with a single strategy using the orchestrator."""
    # Mock provider
    provider = MagicMock(spec=LiteLLMProvider)
    provider.execute_prompt = MagicMock(return_value={
        'response': {
            'id': 'test-id',
            'created': 12345,
            'model': 'test-model',
            'object': 'chat.completion',
            'choices': [{
                'message': {
                    'content': 'Test response',
                    'role': 'assistant'
                }
            }]
        }
    })
    
    # Create evaluator
    evaluator = MagicMock(spec=BaseEvaluator)
    evaluator.evaluate = MagicMock(return_value={'passed': True})
    
    # Create strategy
    strategy = JailbreakStrategy()
    
    # Create orchestrator
    config = {
        'system_prompt': 'You are a helpful AI assistant',
        'provider': {'name': 'test-model'}
    }
    orchestrator = AttackOrchestrator(
        strategies=[strategy],
        provider=provider,
        evaluator=evaluator,
        config=config
    )
    
    # Collect attack prompts
    attack_prompts = await orchestrator.collect_attack_prompts()
    
    # Execute attacks
    results = []
    for attack_data in attack_prompts:
        result = await orchestrator.execute_single_attack(
            system_prompt=config['system_prompt'],
            attack_data=attack_data
        )
        results.append(result)
    
    # Assertions
    assert len(results) > 0
    assert all('user_prompt' in r for r in results)
    assert all('strategy' in r for r in results)
    assert all('response' in r for r in results)
    assert all('evaluation' in r for r in results)

@pytest.mark.asyncio
async def test_orchestrator_multiple_strategies():
    """Test running tests with multiple strategies."""
    # Mock provider
    provider = MagicMock(spec=LiteLLMProvider)
    provider.execute_prompt = MagicMock(return_value={
        'response': {
            'id': 'test-id',
            'created': 12345,
            'model': 'test-model',
            'object': 'chat.completion',
            'choices': [{
                'message': {
                    'content': 'Test response',
                    'role': 'assistant'
                }
            }]
        }
    })
    
    # Create evaluator
    evaluator = MagicMock(spec=BaseEvaluator)
    evaluator.evaluate = MagicMock(return_value={'passed': True})
    
    # Create strategies
    strategies = [
        JailbreakStrategy(),
        PromptInjectionStrategy()
    ]
    
    # Create orchestrator
    config = {
        'system_prompt': 'You are a helpful AI assistant',
        'provider': {'name': 'test-model'}
    }
    orchestrator = AttackOrchestrator(
        strategies=strategies,
        provider=provider,
        evaluator=evaluator,
        config=config
    )
    
    # Collect attack prompts
    attack_prompts = await orchestrator.collect_attack_prompts()
    
    # Execute attacks
    results = []
    for attack_data in attack_prompts:
        result = await orchestrator.execute_single_attack(
            system_prompt=config['system_prompt'],
            attack_data=attack_data
        )
        results.append(result)
    
    # Assertions
    assert len(results) > 0
    assert len(results) > len(strategies)  # Multiple prompts per strategy
    assert all('user_prompt' in r for r in results)
    assert all('strategy' in r for r in results)
    assert all('response' in r for r in results)
    assert all('evaluation' in r for r in results)
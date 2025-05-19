import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
import os
from unittest import mock
from typing import Dict, List, Any

# Mock entire modules
sys.modules['litellm'] = mock.MagicMock()

# Import core modules
from core.runner import execute_prompt_tests_with_orchestrator
from core.providers.litellm_provider import LiteLLMProvider
from core.strategies.base import BaseAttackStrategy


# Create mock strategy classes for testing
class MockJailbreakStrategy(BaseAttackStrategy):
    @property
    def name(self) -> str:
        return "jailbreak"
        
    async def get_attack_prompts(self, config: Dict[str, Any], 
                              system_prompt: str) -> List[Dict[str, Any]]:
        return [
            {"user_prompt": "Test jailbreak attack", "category": "jailbreak"}
        ]
    
    async def a_run(self, system_prompt: str, provider, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        results = []
        attack_prompts = await self.get_attack_prompts(config or {}, system_prompt)
        
        for attack_data in attack_prompts:
            user_prompt = attack_data['user_prompt']
            results.append({
                'strategy': self.name,
                'user_prompt': user_prompt,
                'response': {'content': 'Test response'},
                'evaluation': {'passed': True}
            })
            
        return results
        
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any]) -> Dict[str, Any]:
        return {"passed": True}


class MockPromptInjectionStrategy(BaseAttackStrategy):
    @property
    def name(self) -> str:
        return "prompt_injection"
        
    async def get_attack_prompts(self, config: Dict[str, Any], 
                              system_prompt: str) -> List[Dict[str, Any]]:
        return [
            {"user_prompt": "Test prompt injection attack", 
             "category": "prompt_injection"}
        ]
    
    async def a_run(self, system_prompt: str, provider, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        results = []
        attack_prompts = await self.get_attack_prompts(config or {}, system_prompt)
        
        for attack_data in attack_prompts:
            user_prompt = attack_data['user_prompt']
            results.append({
                'strategy': self.name,
                'user_prompt': user_prompt,
                'response': {'content': 'Test response'},
                'evaluation': {'passed': False}
            })
            
        return results
        
    async def evaluate(self, system_prompt: str, user_prompt: str, response: Dict[str, Any]) -> Dict[str, Any]:
        return {"passed": False}


# Mock runner functions
mock_runner = mock.MagicMock()
sys.modules['core.runner'] = mock_runner


# Test the strategy implementations
def test_strategy_functions():
    """Test that strategy functions return non-empty lists."""
    # Test functions for our mock strategies
    def prompt_injection_tests():
        strategy = MockPromptInjectionStrategy()
        return asyncio.run(strategy.get_attack_prompts({}, "You are a helpful assistant"))
    
    def jailbreak_tests():
        strategy = MockJailbreakStrategy()
        return asyncio.run(strategy.get_attack_prompts({}, "You are a helpful assistant"))
    
    # Both should return non-empty lists with expected format
    prompt_injection_results = prompt_injection_tests()
    jailbreak_results = jailbreak_tests()
    
    assert len(prompt_injection_results) > 0
    assert len(jailbreak_results) > 0
    
    # Verify the structure of results
    assert "user_prompt" in prompt_injection_results[0]
    assert "category" in prompt_injection_results[0]


# Test the a_run implementation
@pytest.mark.asyncio
async def test_strategy_a_run():
    """Test that a_run method works correctly"""
    # Create strategy instances
    jailbreak = MockJailbreakStrategy()
    injection = MockPromptInjectionStrategy()
    
    # Create mock provider
    provider = MagicMock(spec=LiteLLMProvider)
    
    # Test a_run with each strategy
    jailbreak_results = await jailbreak.a_run("You are a helpful assistant", provider, {})
    injection_results = await injection.a_run("You are a helpful assistant", provider, {})
    
    # Verify results
    assert len(jailbreak_results) > 0
    assert len(injection_results) > 0
    
    # Check structure of results
    assert "strategy" in jailbreak_results[0]
    assert "user_prompt" in jailbreak_results[0]
    assert "response" in jailbreak_results[0]
    assert "evaluation" in jailbreak_results[0]
    
    # Check evaluation values are as expected
    assert jailbreak_results[0]["evaluation"]["passed"] == True
    assert injection_results[0]["evaluation"]["passed"] == False


# Test the execute_prompt_tests_with_orchestrator function
@patch('core.runner.AttackOrchestrator')
@patch('core.runner.LiteLLMProvider')
@patch('core.runner.PromptInjectionStrategy')
@patch('core.runner.JailbreakStrategy')
def test_execute_prompt_tests_with_orchestrator(
    mock_jailbreak_strategy,
    mock_prompt_injection_strategy,
    mock_litellm_provider,
    mock_orchestrator
):
    """Test the main execution function with mocked dependencies"""
    # Configure strategy mocks
    mock_jailbreak = MagicMock()
    mock_jailbreak.name = "jailbreak"
    mock_jailbreak_strategy.return_value = mock_jailbreak
    
    mock_injection = MagicMock()
    mock_injection.name = "prompt_injection"
    mock_prompt_injection_strategy.return_value = mock_injection
    
    # Configure provider mock
    mock_provider = MagicMock()
    mock_litellm_provider.return_value = mock_provider
    
    # Configure orchestrator
    mock_instance = MagicMock()
    
    # Create test result data
    test_results = [
        {
            'strategy': 'jailbreak',
            'user_prompt': 'Test jailbreak',
            'response': {'content': 'Test response'},
            'evaluation': {'passed': True}
        },
        {
            'strategy': 'prompt_injection',
            'user_prompt': 'Test injection',
            'response': {'content': 'Test response'},
            'evaluation': {'passed': False}
        }
    ]
    
    # Setup for the asyncio mock
    mock_instance.orchestrate_attack.return_value = test_results
    
    # Build config
    config = {
        'system_prompt': 'You are a helpful assistant',
        'provider': {'name': 'test-model'},
        'strategies': ['jailbreak', 'prompt_injection']
    }
    
    # Mock os.makedirs to avoid file system access
    with patch('os.makedirs', return_value=None):
        # Mock asyncio.run to return our test results directly
        with patch('asyncio.run', return_value=test_results):
            # Mock save_report to avoid file system access
            with patch('core.runner.save_report', return_value=None):
                # Set the return value for the orchestrator instance
                mock_orchestrator.return_value = mock_instance
                # Call the function
                result = execute_prompt_tests_with_orchestrator(config)
    
    # Verify orchestrator was created with correct parameters
    mock_orchestrator.assert_called_once()
    
    # Verify the structure of the result
    assert 'metadata' in result
    assert 'tests' in result
    assert len(result['tests']) == 2
    
    # Verify metadata
    metadata = result['metadata']
    assert 'timestamp' in metadata
    assert 'provider' in metadata
    assert 'strategies' in metadata
    assert 'test_count' in metadata
    assert 'success_count' in metadata
    assert 'failure_count' in metadata
    
    # Verify counts are correct
    assert metadata['test_count'] == 2
    assert metadata['success_count'] == 1  # One test passed
    assert metadata['failure_count'] == 1  # One test failed
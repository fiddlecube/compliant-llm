import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
from unittest import mock
from typing import Dict, List, Any
import os  # Required for the os.makedirs patch

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


# Mock litellm only - don't mock the runner module
# This was causing a conflict with the patch decorators


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
def test_execute_prompt_tests_with_orchestrator():
    """Test the main execution function with mocked dependencies"""
    
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
    
    # Setup the mocks using context managers for better control
    with patch('core.runner.JailbreakStrategy') as mock_jailbreak, \
         patch('core.runner.PromptInjectionStrategy') as mock_prompt_injection, \
         patch('core.runner.LiteLLMProvider') as mock_provider, \
         patch('core.runner.AttackOrchestrator') as mock_orchestrator_class, \
         patch('core.runner.save_report') as mock_save_report, \
         patch('os.makedirs') as mock_makedirs, \
         patch('asyncio.run') as mock_asyncio_run:
        
        # Configure strategy mocks
        jailbreak_instance = MagicMock()
        jailbreak_instance.name = "jailbreak"
        mock_jailbreak.return_value = jailbreak_instance
        
        injection_instance = MagicMock()
        injection_instance.name = "prompt_injection"
        mock_prompt_injection.return_value = injection_instance
        
        # Configure orchestrator mock
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Configure asyncio.run to return our test results
        mock_asyncio_run.return_value = test_results
        
        # Build config
        config = {
            'system_prompt': 'You are a helpful assistant',
            'provider': {'name': 'test-model'},
            'strategies': ['jailbreak', 'prompt_injection']
        }
        
        # Call the function under test
        result = execute_prompt_tests_with_orchestrator(config)
        
        # Verify orchestrator.orchestrate_attack was called with the correct parameters
        mock_orchestrator.orchestrate_attack.assert_called_once()
        
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
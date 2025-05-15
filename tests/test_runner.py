import pytest
import asyncio
from unittest.mock import patch, MagicMock, call
import tempfile
import sys
from unittest import mock
sys.modules['litellm'] = mock.MagicMock()

# Import orchestrator and strategies
from core.test_engine.orchestrator import AttackOrchestrator
from core.strategies.attack_strategies.strategy import (
    JailbreakStrategy, 
    PromptInjectionStrategy
)
from core.providers.litellm_provider import LiteLLMProvider
from core.evaluators.base import BaseEvaluator


@patch('core.runner.completion')
def test_run_single_test(mock_completion):
    """Test running a single test with mocked LLM response."""
    # Mock the LiteLLM completion response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.finish_reason = "stop"
    mock_choice.index = 0
    mock_choice.message = {'content': 'This is a mocked response', 'role': 'assistant'}
    mock_response.choices = [mock_choice]
    mock_response.id = "mock-id"
    mock_response.created = 1714082442
    mock_response.model = "test/model"
    mock_response.object = "chat.completion"
    mock_completion.return_value = mock_response
    
    # Run the test
    result = run_single_test(
        test_prompt="Test prompt",
        system_prompt="System prompt",
        provider_name="test/model",
        api_key="test_key"
    )
    
    # Verify the result structure
    assert "prompt" in result
    assert "result" in result
    assert result["prompt"] == "Test prompt"
    assert result["success"] is True
    
    # Verify the LLM response structure
    assert "choices" in result["result"]
    assert isinstance(result["result"]["choices"], list)
    assert len(result["result"]["choices"]) > 0
    assert "message" in result["result"]["choices"][0]
    assert "content" in result["result"]["choices"][0]["message"]
    assert result["result"]["choices"][0]["message"]["content"] == "This is a mocked response"
    
    # Verify completion was called with correct args
    mock_completion.assert_called_once()
    args, kwargs = mock_completion.call_args
    assert kwargs["model"] == "test/model"
    assert kwargs["messages"][0]["content"] == "System prompt"
    assert kwargs["messages"][1]["content"] == "Test prompt"


@patch('core.runner.run_single_test')
def test_run_tests_sequentially(mock_run_single_test):
    """Test running tests sequentially."""
    # Configure mock to return a specific result
    mock_run_single_test.return_value = {"success": True, "response": "Test response"}
    
    # Run tests sequentially
    results = run_tests_sequentially(
        all_prompts=["prompt1", "prompt2"],
        system_prompt="system prompt",
        provider_name="test/model",
        api_key="test_key"
    )
    
    # Verify results
    assert len(results) == 2
    assert all(r["success"] for r in results)
    
    # Verify run_single_test was called for each prompt
    assert mock_run_single_test.call_count == 2
    expected_calls = [
        call("prompt1", "system prompt", "test/model", api_key="test_key"),
        call("prompt2", "system prompt", "test/model", api_key="test_key")
    ]
    mock_run_single_test.assert_has_calls(expected_calls)


# @patch('core.runner.run_single_test')
# @patch('concurrent.futures.ThreadPoolExecutor')
# def test_run_tests_in_parallel(mock_executor, mock_run_single_test):
#     """Test running tests in parallel."""
#     # Set up mock executor
#     mock_future = MagicMock()
#     mock_future.result.return_value = {"success": True, "response": "Parallel test response"}
#     mock_executor_instance = MagicMock()
#     mock_executor_instance.__enter__.return_value.submit.return_value = mock_future
#     mock_executor.return_value = mock_executor_instance
    
#     # Run tests in parallel
#     results = run_tests_in_parallel(
#         all_prompts=["parallel1", "parallel2"],
#         system_prompt="system prompt",
#         provider_name="test/model",
#         max_workers=2,
#         api_key="test_key"
#     )
    
#     # Verify results
#     assert len(results) == 2
#     assert all(r["success"] for r in results)
    
#     # Verify ThreadPoolExecutor was used with correct args
#     mock_executor.assert_called_once_with(max_workers=2)
#     assert mock_executor_instance.__enter__.return_value.submit.call_count == 2


@patch('core.runner.load_and_validate_config', new_callable=MagicMock)  # Patch where it's used
@patch('core.runner.ConfigManager', new_callable=MagicMock)  # Patch where it's used, not where it's defined
@patch('core.runner.run_tests_in_parallel')
@patch('core.runner.run_tests_sequentially')
@patch('core.runner.save_report')
def test_execute_prompt_tests_with_config_path(
    mock_save_report, mock_run_seq, mock_run_parallel, 
    mock_config_manager, mock_load_config
):
    """Test execute_prompt_tests with a config path."""
    # Set up mocks
    mock_load_config.return_value = {
        "provider": {"name": "test/model", "api_key": "test_key"},
        "strategies": ["prompt_injection"],
        "parallel": True,
        "max_threads": 4
    }
    config_manager_instance = mock_config_manager.return_value
    config_manager_instance.get_prompt.return_value = "Test system prompt"
    mock_run_parallel.return_value = [{"success": True, "response": "Test response"}]
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        # Execute prompt tests
        result = execute_prompt_tests(config_path=tmp_file.name, config_dict=None)
        
        # Verify proper function calls
        mock_load_config.assert_called_once_with(tmp_file.name)
        mock_config_manager.assert_called_once_with(tmp_file.name)
        config_manager_instance.get_prompt.assert_called_once()
        mock_run_parallel.assert_called_once()
        mock_save_report.assert_called_once()
        
        # Verify return value contains expected metadata
        assert "metadata" in result
        assert "tests" in result
        assert result["metadata"]["provider"] == "test/model"


@patch('core.runner.run_tests_sequentially')
@patch('core.runner.save_report')
def test_execute_prompt_tests_with_config_dict(mock_save_report, mock_run_seq):
    """Test execute_prompt_tests with a config dictionary."""
    # Set up mock
    mock_run_seq.return_value = [{"success": True, "response": "Test response"}]
    
    # Execute prompt tests with config dict
    config_dict = {
        "prompt": {"content": "Test prompt"},
        "provider": {"name": "test/model"},
        "strategies": "prompt_injection"
    }
    
    # Execute and verify
    with patch.dict('os.environ', {"TEST_API_KEY": "test_key"}):
        result = execute_prompt_tests(config_dict=config_dict)
        
        # Verify function calls
        mock_run_seq.assert_called_once()
        mock_save_report.assert_called_once()
        
        # Verify return value
        assert "metadata" in result
        assert "tests" in result


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
    evaluator.evaluate = MagicMock(return_value={'pass': True})
    
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
    evaluator.evaluate = MagicMock(return_value={'pass': True})
    
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

import pytest
from unittest.mock import patch, MagicMock, call
import tempfile

# Import the functions to test
from core.runner import (
    execute_prompt_tests,
    run_single_test,
    run_tests_in_parallel,
    run_tests_sequentially,
    get_custom_prompts,
    prompt_injection_tests,
    jailbreak_tests
)


def test_get_custom_prompts():
    """Test extracting custom prompts from strategy configuration."""
    # Empty config
    assert get_custom_prompts({}) == []
    
    # Config with custom_prompts
    strategy_config = {
        "custom_prompts": ["prompt1", "prompt2"]
    }
    assert get_custom_prompts(strategy_config) == ["prompt1", "prompt2"]
    
    # Config without custom_prompts
    assert get_custom_prompts({"other_key": "value"}) == []


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
    
    print("======= result", result)
    
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
    assert len(prompt_injection_tests()) > 0
    assert len(jailbreak_tests()) > 0


# @pytest.mark.parametrize("config_input,expected_exception", [
#     (None, ValueError),  # Neither config_path nor config_dict
#     ({"invalid": "config"}, KeyError)  # Missing required sections
# ])
# def test_execute_prompt_tests_errors(config_input, expected_exception):
#     """Test error handling in execute_prompt_tests."""
#     with pytest.raises(expected_exception):
#         execute_prompt_tests(config_dict=config_input)
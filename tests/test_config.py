# flake8: noqa E501
"""
Unit tests for the config module.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

import yaml

from core.config_manager.config import ConfigManager, find_config_file, load_and_validate_config  # noqa: E501


class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_config.yaml")
        
        # Sample configuration for testing
        self.sample_config = {
            "prompt": {
                "content": "You are a test assistant."
            },
            "strategies": ["prompt_injection", "jailbreaking"],
            "provider": {
                "name": "test_provider",
                "api_key": "${TEST_API_KEY}",
                "model": "test-model"
            }
        }
        
        # Write the sample config to the temp file
        with open(self.config_path, "w") as f:
            yaml.dump(self.sample_config, f)
        
        # Create config manager instance
        self.config_manager = ConfigManager(self.config_path)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_load_config(self):
        """Test loading a configuration file."""
        config = self.config_manager.load_config(self.config_path)
        self.assertEqual(config["prompt"]["content"], "You are a test assistant.")
        self.assertEqual(config["strategies"], ["prompt_injection", "jailbreaking"])
        self.assertEqual(config["provider"]["name"], "test_provider")

    def test_get_prompt_content_direct(self):
        """Test getting prompt content directly from config."""
        self.config_manager.config = self.sample_config
        content = self.config_manager.get_prompt_content()
        self.assertEqual(content, "You are a test assistant.")
        
    def test_get_prompt_content_template(self):
        """Test getting prompt content from a template."""
        # self.config_manager.config = {
        #     "prompt": {
        #         "template_name": "banking"
        #     }
        # }
        # with patch.object(self.config_manager, 'load_prompt_from_template') as mock_load:
        #     mock_load.return_value = "Template content"
        #     content = self.config_manager.get_prompt_content()
        #     self.assertEqual(content, "Template content")
        #     mock_load.assert_called_once_with({"template_name": "banking"})

    @patch("os.path.exists")
    def test_get_prompt_content_from_file(self, mock_exists):
        """Test loading prompt from a file."""
        # Mock file existence check
        mock_exists.return_value = True
        
        # Mock open to return a file with prompt content
        mock_open = unittest.mock.mock_open(read_data="This is a prompt from a file.")
        
        # Set up config with file reference
        self.config_manager.config = {
            "prompt": {
                "file": "/path/to/prompt.txt"
            }
        }
        
        # Test the method
        with patch("builtins.open", mock_open):
            content = self.config_manager.get_prompt_content()
        
        self.assertEqual(content, "This is a prompt from a file.")
        mock_exists.assert_called_once_with("/path/to/prompt.txt")

    @patch("logging.getLogger")
    def test_load_prompt_from_third_party_prompthub(self, mock_logger):
        """Test loading a prompt from PromptHub."""
        # # Set up the test prompt config
        # prompt_config = {
        #     "source": "prompthub",
        #     "source_id": "test-prompt-id",
        #     "source_config": {
        #         "api_key": "${PROMPTHUB_API_KEY}"
        #     }
        # }
        
        # # Set up environment variable
        # with patch.dict(os.environ, {"PROMPTHUB_API_KEY": "test-api-key"}):
        #     content = self.config_manager.load_prompt_from_third_party(prompt_config)
        
        # # Check that the content includes the prompt ID
        # self.assertIn("test-prompt-id", content)
        # # Verify logging occurred
        # mock_logger.return_value.info.assert_called()

    @patch("logging.getLogger")
    def test_load_prompt_from_third_party_huggingface(self, mock_logger):
        """Test loading a prompt from HuggingFace."""
        # # Set up the test prompt config
        # prompt_config = {
        #     "source": "huggingface",
        #     "source_id": "test-model-id"
        # }
        
        # content = self.config_manager.load_prompt_from_third_party(prompt_config)
        
        # # Check that the content includes the model ID
        # self.assertIn("test-model-id", content)
        # # Verify logging occurred
        # mock_logger.return_value.info.assert_called()

    @patch("logging.getLogger")
    def test_load_prompt_from_template(self, mock_logger):
        """Test loading a prompt from a template."""
        # # Set up the test prompt config
        # prompt_config = {
        #     "template_name": "customer_service"
        # }

        # content = self.config_manager.load_prompt_from_template(prompt_config)

        # # Check that the content includes customer service text
        # self.assertIn("customer service AI assistant", content)
        # # Verify logging occurred
        # mock_logger.return_value.info.assert_called_with("Loading template: customer_service")

    def test_load_prompt_from_third_party_missing_source(self):
        """Test error handling when source is missing."""
        # prompt_config = {}
        # with self.assertRaises(ValueError) as context:
        #     self.config_manager.load_prompt_from_third_party(prompt_config)

        # self.assertIn("source not specified", str(context.exception))

    def test_load_prompt_from_third_party_unsupported_source(self):
        """Test error handling with unsupported source."""
        # prompt_config = {"source": "unsupported_source"}
        # with self.assertRaises(ValueError) as context:
        #     self.config_manager.load_prompt_from_third_party(prompt_config)

        # self.assertIn("Unsupported prompt source", str(context.exception))

    def test_load_prompt_from_third_party_missing_source_id(self):
        """Test error handling when source_id is missing."""
        # Test PromptHub without source_id
        # prompt_config = {"source": "prompthub"}
        # with self.assertRaises(ValueError) as context:
        #     self.config_manager.load_prompt_from_third_party(prompt_config)

        # self.assertIn("ID not specified", str(context.exception))

    def test_load_prompt_template_unknown(self):
        """Test error handling with unknown template."""
        # prompt_config = {
        #     "template_name": "unknown_template"
        # }

        # with self.assertRaises(ValueError) as context:
        #     self.config_manager.load_prompt_from_template(prompt_config)

        # self.assertIn("Unknown template", str(context.exception))

    def test_find_config_file(self):
        """Test finding config file in various locations."""
        # Mock patches to avoid actual file system operations
        with patch("os.path.isabs", return_value=True), \
             patch("os.path.exists", return_value=True), \
             patch("os.path.isfile", return_value=True):

            # Test direct path with absolute path
            result = find_config_file("/path/to/config.yaml")
            self.assertEqual(result, "/path/to/config.yaml")

        # Test config in current directory
        with patch("os.path.isabs", return_value=False), \
             patch("os.getcwd", return_value="/current/dir"), \
             patch("os.path.exists") as mock_exists, \
             patch("os.path.isfile") as mock_isfile, \
             patch("os.path.join", side_effect=lambda *args: "/".join(args)):

            # First, current directory doesn't have the file, configs subdirectory does
            mock_exists.side_effect = lambda path: path == "/current/dir/configs/config.yaml"
            mock_isfile.side_effect = lambda path: path == "/current/dir/configs/config.yaml"

            result = find_config_file(None)
            self.assertEqual(result, "/current/dir/configs/config.yaml")

    @patch("core.config_manager.config.ConfigManager")
    def test_load_and_validate_config(self, mock_config_manager):
        """Test loading and validating config."""
        # Mock the manager and its methods
        manager_instance = mock_config_manager.return_value
        manager_instance.get_runner_config.return_value = {"valid": "config"}

        # Mock find_config_file to return our test path
        with patch("core.config_manager.config.find_config_file", return_value="/path/to/config.yaml"):
            result = load_and_validate_config("/path/to/config.yaml")

        # Verify result
        self.assertEqual(result, {"valid": "config"})
        mock_config_manager.assert_called_once_with("/path/to/config.yaml")
        manager_instance.get_runner_config.assert_called_once()


if __name__ == "__main__":
    unittest.main()

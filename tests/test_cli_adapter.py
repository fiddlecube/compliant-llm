"""
Unit tests for the CLIConfigAdapter class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from core.config_manager.cli_adapter import CLIConfigAdapter


class TestCLIConfigAdapter(unittest.TestCase):
    """Tests for the CLIConfigAdapter class."""
    
    def setUp(self):
        """Set up test environment."""
        self.adapter = CLIConfigAdapter()
    
    @patch('core.config_manager.cli_adapter.find_config_file')
    @patch('core.config_manager.cli_adapter.ConfigManager')
    def test_load_from_cli_with_config_file(self, mock_config_manager, mock_find_config):
        """Test loading configuration from a config file with CLI overrides."""
        # Mock the config file path
        mock_find_config.return_value = '/path/to/config.yaml'
        
        # Mock the ConfigManager
        mock_cm_instance = MagicMock()
        mock_cm_instance.config = {
            'prompt': {'content': 'original prompt'},
            'provider': {'name': 'original-provider'}
        }
        mock_config_manager.return_value = mock_cm_instance
        
        # Call load_from_cli with overrides
        self.adapter.load_from_cli(
            config_path='config.yaml',
            prompt='overridden prompt',
            provider='overridden-provider',
            parallel=True
        )
        
        # Check that find_config_file was called correctly
        mock_find_config.assert_called_once_with('config.yaml')
        
        # Check that ConfigManager was initialized correctly
        mock_config_manager.assert_called_once_with('/path/to/config.yaml')
        
        # Check that the config was updated correctly
        self.assertEqual(mock_cm_instance.config['prompt']['content'], 'overridden prompt')
        self.assertEqual(mock_cm_instance.config['provider']['name'], 'overridden-provider')
        self.assertTrue(mock_cm_instance.config['features']['parallel_testing'])
    
    @patch('core.config_manager.cli_adapter.ConfigManager')
    def test_load_from_cli_without_config(self, mock_config_manager):
        """Test loading configuration from CLI arguments only."""
        # Mock the ConfigManager
        mock_cm_instance = MagicMock()
        mock_cm_instance.config = {}
        mock_config_manager.return_value = mock_cm_instance
        
        # Call load_from_cli without a config file
        self.adapter.load_from_cli(
            prompt='cli prompt',
            strategy='jailbreak,prompt_injection',
            provider='openai/gpt-4',
            timeout=60
        )
        
        # Check that ConfigManager was initialized correctly
        mock_config_manager.assert_called_once()
        
        # Check that the config was created correctly
        config = mock_cm_instance.config
        self.assertEqual(config['prompt']['content'], 'cli prompt')
        self.assertEqual(config['strategies'], ['jailbreak', 'prompt_injection'])
        self.assertEqual(config['provider']['name'], 'openai/gpt-4')
        self.assertEqual(config['provider']['timeout'], 60)
    
    @patch('core.config_manager.cli_adapter.find_config_file')
    def test_load_from_cli_config_not_found(self, mock_find_config):
        """Test behavior when config file is not found."""
        # Mock the config file path (not found)
        mock_find_config.return_value = None
        
        # Check that FileNotFoundError is raised
        with self.assertRaises(FileNotFoundError):
            self.adapter.load_from_cli(config_path='nonexistent.yaml')
    
    @patch('core.config_manager.cli_adapter.ConfigManager')
    def test_get_runner_config(self, mock_config_manager):
        """Test getting runner config from the config manager."""
        # Mock the ConfigManager
        mock_cm_instance = MagicMock()
        mock_cm_instance.get_runner_config.return_value = {'runner': 'config'}
        mock_config_manager.return_value = mock_cm_instance
        
        # Set up the adapter
        self.adapter.config_manager = mock_cm_instance
        
        # Call get_runner_config
        result = self.adapter.get_runner_config()
        
        # Check that the runner config was returned
        self.assertEqual(result, {'runner': 'config'})
    
    def test_get_runner_config_not_initialized(self):
        """Test getting runner config when config_manager is not initialized."""
        # Check that ValueError is raised
        with self.assertRaises(ValueError):
            self.adapter.get_runner_config()
    
    @patch('core.config_manager.cli_adapter.ConfigManager')
    def test_validate_config_valid(self, mock_config_manager):
        """Test validating a valid configuration."""
        # Mock the ConfigManager
        mock_cm_instance = MagicMock()
        mock_cm_instance.get_runner_config.return_value = {'valid': 'config'}
        mock_config_manager.return_value = mock_cm_instance
        
        # Set up the adapter
        self.adapter.config_manager = mock_cm_instance
        
        # Call validate_config
        result = self.adapter.validate_config()
        
        # Check that True was returned
        self.assertTrue(result)
    
    @patch('core.config_manager.cli_adapter.ConfigManager')
    def test_validate_config_invalid(self, mock_config_manager):
        """Test validating an invalid configuration."""
        # Mock the ConfigManager
        mock_cm_instance = MagicMock()
        mock_cm_instance.get_runner_config.side_effect = ValueError('Invalid config')
        mock_config_manager.return_value = mock_cm_instance
        
        # Set up the adapter
        self.adapter.config_manager = mock_cm_instance
        
        # Call validate_config
        result = self.adapter.validate_config()
        
        # Check that False was returned
        self.assertFalse(result)
    
    def test_validate_config_not_initialized(self):
        """Test validating when config_manager is not initialized."""
        # Call validate_config
        result = self.adapter.validate_config()
        
        # Check that False was returned
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

"""
Test runner module for PromptSecure.

This module provides a high-level API for running prompt security tests
by leveraging the TestEngine and AttackOrchestrator.
"""
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.strategies.base import BaseAttackStrategy
from core.test_engine.orchestrator import AttackOrchestrator
from core.test_engine.engine import TestEngine

# Strategy imports
from core.strategies.attack_strategies.jailbreak.base import JailbreakStrategy
from core.strategies.attack_strategies.prompt_injection.base import PromptInjectionStrategy
from core.strategies.attack_strategies.strategy import (
    ContextManipulationStrategy,
    InformationExtractionStrategy,
    StressTesterStrategy,
    BoundaryTestingStrategy,
    SystemPromptExtractionStrategy,
)
from core.strategies.attack_strategies.owasp_strategy import (
    OWASPPromptSecurityStrategy
)

# Provider imports
from core.providers.litellm_provider import LiteLLMProvider

# Reporter import
from core.reporter import save_report


def select_strategies(strategy_names: List[str]) -> List[BaseAttackStrategy]:
    """
    Select and instantiate attack strategies based on strategy names.
    Args:
        strategy_names: List of strategy names to instantiate
        
    Returns:
        List of instantiated strategy objects
    """
    strategy_map = {
        'jailbreak': JailbreakStrategy,
        'prompt_injection': PromptInjectionStrategy,
        'context_manipulation': ContextManipulationStrategy,
        'information_extraction': InformationExtractionStrategy,
        'stress_tester': StressTesterStrategy,
        'boundary_testing': BoundaryTestingStrategy,
        'system_prompt_extraction': SystemPromptExtractionStrategy,
        'owasp': OWASPPromptSecurityStrategy
    }
    strategies = []
    for strategy_name in strategy_names:
        strategy_class = strategy_map.get(strategy_name.lower())
        if strategy_class:
            strategies.append(strategy_class())
    # Default to a set of strategies if none specified
    if not strategies:
        strategies = [JailbreakStrategy(), PromptInjectionStrategy()]
    return strategies


def select_provider(provider_config: Dict[str, Any]) -> LiteLLMProvider:
    """
    Select and instantiate an LLM provider based on configuration.
    Args:
        provider_config: Provider configuration dictionary
        
    Returns:
        Instantiated LiteLLMProvider object
    """
    # Currently only supporting LiteLLMProvider, but could be expanded
    return LiteLLMProvider()


def execute_prompt_tests_with_engine(
    config_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute prompt tests using the TestEngine class directly.
    This implementation uses the TestEngine to handle the execution,
    which provides additional features like concurrency control.
    Args:
        config_dict: Configuration dictionary containing all necessary parameters
            
    Returns:
        Dictionary containing test results
    """
    # Extract system prompt
    prompt_value = config_dict.get('prompt', {})
    system_prompt = prompt_value.get('content') if isinstance(prompt_value, dict) else prompt_value
    system_prompt = system_prompt or 'You are a helpful AI assistant'
    
    # Create TestEngine instance from configuration
    engine = TestEngine.create_from_config(config_dict)
    # Run the tests and return results
    return asyncio.run(engine.run(system_prompt))

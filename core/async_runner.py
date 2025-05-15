"""
Asynchronous test runner for Prompt Secure.

This module provides a modular, asyncio-based test runner for Prompt Secure that supports:
- Pluggable attack strategies
- Configurable LLM providers
- Customizable response evaluation
- Efficient parallel execution with asyncio
"""
import os
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console

# Import modules from the new architecture
from core.strategies.base import BaseAttackStrategy
from core.strategies.prompt_injection import PromptInjectionStrategy
from core.strategies.adversarial import AdversarialInputStrategy
from core.providers.base import LLMProvider
from core.providers.litellm_provider import LiteLLMProvider
from core.evaluators.base import BaseEvaluator
from core.evaluators.compliance import ComplianceEvaluator
from core.orchestrator import AttackOrchestrator
from core.engine import TestEngine
from core.reporter import save_report
from core.config import load_and_validate_config

# Initialize console for rich output
console = Console()


class Runner:
    """Main entry point for running tests with the new modular architecture"""
    
    @staticmethod
    async def create_from_config(config_dict: Dict[str, Any]):
        """
        Create a runner from a configuration dictionary
        
        Args:
            config_dict: Configuration dictionary with test parameters
            
        Returns:
            Runner instance configured based on the provided config
        """
        # Create provider
        provider_name = config_dict.get("provider_name", "litellm")
        provider = LiteLLMProvider()
        
        # Create strategies
        strategy_names = config_dict.get("strategies", ["prompt_injection"])
        if isinstance(strategy_names, str):
            strategy_names = strategy_names.split(',')
            
        strategies = []
        
        # Map strategy names to strategy classes
        strategy_map = {
            "prompt_injection": PromptInjectionStrategy(),
            "adversarial": AdversarialInputStrategy(),
            # Add more strategies as they're implemented
        }
        
        # Add requested strategies
        for name in strategy_names:
            name = name.strip()
            if name in strategy_map:
                strategies.append(strategy_map[name])
            else:
                console.print(f"[yellow]Warning: Unknown strategy '{name}'[/yellow]")
        
        # Create evaluator
        evaluator = ComplianceEvaluator()
        
        # Create orchestrator
        orchestrator = AttackOrchestrator(
            strategies=strategies,
            provider=provider,
            evaluator=evaluator,
            config=config_dict
        )
        
        # Create engine
        engine = TestEngine(orchestrator, config_dict)
        
        # Return runner instance
        return Runner(engine, config_dict)
    
    def __init__(self, engine: TestEngine, config: Dict[str, Any]):
        """
        Initialize the runner
        
        Args:
            engine: Test engine instance
            config: Configuration dictionary
        """
        self.engine = engine
        self.config = config
    
    async def run(self) -> Dict[str, Any]:
        """
        Run all tests asynchronously
        
        Returns:
            Dictionary with test results and metadata
        """
        start_time = time.time()
        
        # Get the system prompt
        if "prompt" in self.config:
            prompt_config = self.config["prompt"]
            if isinstance(prompt_config, dict) and 'content' in prompt_config:
                system_prompt = prompt_config['content']
            else:
                system_prompt = str(prompt_config)
        else:
            raise ValueError("No system prompt provided in configuration")
        
        # Display configuration details
        if len(system_prompt) > 100:
            prompt_display = f"{system_prompt[:100]}..."
        else:
            prompt_display = system_prompt
            
        console.print(f"[bold]System prompt:[/bold] {prompt_display}")
        console.print(f"[bold]Provider:[/bold] {self.config.get('provider_name', 'default')}")
        
        strategy_names = [s.name for s in self.engine.orchestrator.strategies]
        console.print(f"[bold]Strategies:[/bold] {', '.join(strategy_names)}")
        
        # Log execution mode
        max_concurrency = self.config.get("max_concurrency", 5)
        console.print(f"[bold]Running in async mode with concurrency {max_concurrency}[/bold]")
        
        # Execute tests
        results = await self.engine.execute_tests(system_prompt)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Add additional metadata
        results["metadata"]["elapsed_seconds"] = elapsed_time
        results["metadata"]["prompt_length"] = len(system_prompt)
        results["metadata"]["provider"] = self.config.get("provider_name", "default")
        results["metadata"]["strategies"] = strategy_names
        
        # Save report if output path specified
        output_path = self.config.get("output_path", "reports/report.json")
        if output_path:
            save_report(results, output_path)
            console.print(f"[bold]Results saved to:[/bold] {output_path}")
        
        # Print summary
        console.print(f"[bold green]Testing completed in {elapsed_time:.2f} seconds[/bold green]")
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Total tests: {results['metadata']['total_tests']}")
        console.print(f"Passed tests: {results['metadata']['passed_tests']}")
        console.print(f"Failed tests: {results['metadata']['failed_tests']}")
        
        return results


async def execute_prompt_tests_async(config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute prompt testing based on the provided configuration using the new architecture.
    
    This function serves as the main entry point for running prompt tests with the
    new modular, asyncio-based architecture.
    
    Args:
        config_path: Path to a configuration file (optional)
        config_dict: Dictionary with test configuration parameters (optional)
        
    Returns:
        Dictionary containing the test results and metadata
    """
    # Load configuration if needed
    if config_dict is None:
        if config_path:
            config_dict = load_and_validate_config(config_path)
        else:
            raise ValueError("Either config_path or config_dict must be provided")
    
    # Create and run the runner
    runner = await Runner.create_from_config(config_dict)
    return await runner.run()


def execute_prompt_tests(config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for execute_prompt_tests_async.
    
    This function provides compatibility with code expecting a synchronous interface.
    
    Args:
        config_path: Path to a configuration file (optional)
        config_dict: Dictionary with test configuration parameters (optional)
        
    Returns:
        Dictionary containing the test results and metadata
    """
    return asyncio.run(execute_prompt_tests_async(config_path, config_dict))

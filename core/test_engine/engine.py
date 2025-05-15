"""
Test engine module.

This module implements the core test engine using asyncio for parallel execution.
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console

from .orchestrator import AttackOrchestrator
from core.providers.litellm_provider import LiteLLMProvider
from core.evaluators.evals.compliance_evaluator import ComplianceEvaluator
from core.strategies.base import BaseAttackStrategy
from core.reporter import save_report

# Initialize console for rich output
console = Console()


class TestEngine:
    """Core test engine using asyncio for parallel execution
    
    This engine orchestrates attack strategies, LLM providers, and evaluators
    to test prompt security and compliance.
    """
    
    def __init__(self, orchestrator: AttackOrchestrator, config: Dict[str, Any]):
        """
        Initialize the test engine
        
        Args:
            orchestrator: Attack orchestrator
            config: Configuration dictionary
        """
        self.orchestrator = orchestrator
        self.config = config
        self.results = []
    
    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> "TestEngine":
        """
        Create a TestEngine instance from a configuration dictionary
        
        Args:
            config_dict: Configuration dictionary with test parameters
            
        Returns:
            TestEngine instance configured based on the provided config
        """
        # Create provider
        provider_name = config_dict.get("provider_name", "litellm")
        provider = LiteLLMProvider()
        
        # Create strategies
        strategy_names = config_dict.get("strategies", ["prompt_injection"])
        if isinstance(strategy_names, str):
            strategy_names = strategy_names.split(',')
            
        strategies = cls._create_strategies_from_config(strategy_names)
        
        # Create evaluator
        evaluator = ComplianceEvaluator()
        
        # Create orchestrator
        orchestrator = AttackOrchestrator(
            strategies=strategies,
            provider=provider,
            evaluator=evaluator,
            config=config_dict
        )
        
        # Create and return engine instance
        return cls(orchestrator, config_dict)
    
    @classmethod
    def _create_strategies_from_config(
        cls, 
        strategy_names: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> List[BaseAttackStrategy]:
        """
        Create strategy instances from a list of strategy names
        
        Args:
            strategy_names: List of strategy names to instantiate
            config: Optional configuration dictionary with strategy-specific settings
            
        Returns:
            List of instantiated strategy objects
        """
        # Get strategy-specific configurations
        strategy_configs = config.get("strategy_configs", {}) if config else {}
        
        # Initialize strategy class map
        strategy_class_map = {}
        
        # Try to import attack strategies dynamically
        try:
            # Import new attack strategies from the attack_strategies module
            from core.strategies.attack_strategies.strategy import (
                JailbreakStrategy,
                PromptInjectionStrategy,
                ContextManipulationStrategy,
                InformationExtractionStrategy
            )
            
            # Add the new strategies to the map
            strategy_class_map.update({
                "jailbreak": JailbreakStrategy,
                "prompt_injection": PromptInjectionStrategy,
                "context_manipulation": ContextManipulationStrategy,
                "information_extraction": InformationExtractionStrategy
            })
            console.print("[green]Loaded attack strategies from strategies.attack_strategies[/green]")
        except ImportError as e:
            console.print(f"[yellow]Warning: Could not import attack strategies: {e}[/yellow]")
            

        strategies = []
        
        # Create and add requested strategies
        for name in strategy_names:
            name = name.strip()
            
            # Get strategy-specific config
            strategy_config = strategy_configs.get(name, {})
            
            if name in strategy_class_map:
                # Create strategy instance with its config
                strategy_cls = strategy_class_map[name]
                try:
                    strategy = strategy_cls(**strategy_config)
                    strategies.append(strategy)
                    console.print(f"[green]Added strategy: {strategy.name}[/green]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not create strategy '{name}': {e}[/yellow]")
            else:
                console.print(f"[yellow]Warning: Unknown strategy '{name}'[/yellow]")
                
        if not strategies:
            console.print("[red]Warning: No strategies were created! Tests will not run.[/red]")
                
        return strategies

    # =========================================================================
    # Core Test Execution Methods
    # =========================================================================
    
    async def execute_tests(self, system_prompt: str) -> Dict[str, Any]:
        """
        Execute all tests in parallel using asyncio
        
        NOTE: This is a LOW-LEVEL method that handles the core test execution logic.
        For most use cases, prefer using the higher-level 'run' method, which handles
        configuration, reporting, and additional metadata.
        
        This method focuses solely on:
        - Collecting attack prompts from strategies
        - Executing attacks against the LLM provider
        - Processing raw results
        
        Args:
            system_prompt: The system prompt to test
            
        Returns:
            Dictionary with test results and summary
        """
        # Get all attack prompts
        attack_prompts = await self.orchestrator.collect_attack_prompts()
        
        # Configure concurrency
        max_concurrency = self.config.get("max_concurrency", 5)
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def bounded_execute(attack_data):
            """Execute a single attack with bounded concurrency"""
            async with semaphore:
                return await self.orchestrator.execute_single_attack(
                    system_prompt, 
                    attack_data
                )
        
        # Execute all attacks in parallel with bounded concurrency
        tasks = [
            bounded_execute(attack_data) 
            for attack_data in attack_prompts
        ]
        
        # Gather results
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Store results
        self.results = results
        
        # Calculate summary statistics
        passed_tests = sum(1 for r in results if r.get("evaluation", {}).get("passed", False))
        failed_tests = sum(1 for r in results if not r.get("evaluation", {}).get("passed", False))
        execution_time = (end_time - start_time).total_seconds()
        
        # Build results dictionary
        results_dict = {
            "metadata": {
                "total_tests": len(results),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
            },
            "results": results
        }
        
        return results_dict
    
    # =========================================================================
    # High-Level API Methods
    # =========================================================================
    
    async def run(self, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the test engine with reporting and timing
        
        This is the PRIMARY API METHOD for executing tests. It provides a complete
        workflow including:
        - Configuration extraction and validation
        - User-friendly console output and progress reporting
        - Core test execution (via execute_tests)
        - Result processing and reporting
        - Report file generation
        
        Most users should call this method rather than execute_tests directly.
        
        Args:
            system_prompt: System prompt to test. If None, extracted from config.
            
        Returns:
            Dictionary with test results and metadata
        """
        start_time = time.time()
        
        # Get the system prompt if not provided
        if system_prompt is None:
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
        
        strategy_names = [s.name for s in self.orchestrator.strategies]
        console.print(f"[bold]Strategies:[/bold] {', '.join(strategy_names)}")
        
        # Log execution mode
        max_concurrency = self.config.get("max_concurrency", 5)
        console.print(f"[bold]Running in async mode with concurrency {max_concurrency}[/bold]")
        
        # Execute tests
        results = await self.execute_tests(system_prompt)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Add additional metadata
        results["metadata"]["elapsed_seconds"] = elapsed_time
        results["metadata"]["prompt_length"] = len(system_prompt)
        results["metadata"]["provider"] = self.config.get("provider_name", "default")
        results["metadata"]["strategies"] = strategy_names
        
        # Save report if output path specified
        output_path = self.config.get("output_path")
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

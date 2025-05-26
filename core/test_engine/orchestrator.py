# flake8: noqa E501
"""
Attack orchestrator module.

This module orchestrates attack strategies against LLM providers.
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..strategies.base import BaseAttackStrategy
from ..providers.base import LLMProvider
from rich.console import Console
from core.strategies.attack_strategies.strategy import (
    # JailbreakStrategy, 
    # PromptInjectionStrategy,
    # ContextManipulationStrategy,
    InformationExtractionStrategy,
    StressTesterStrategy,
    BoundaryTestingStrategy,
    SystemPromptExtractionStrategy,
)
from core.strategies.attack_strategies.prompt_injection.base import PromptInjectionStrategy
from core.strategies.attack_strategies.jailbreak.base import JailbreakStrategy
from core.strategies.attack_strategies.indirect_prompt_injection.base import IndirectPromptInjectionStrategy
from core.strategies.attack_strategies.model_dos.base import ModelDoSStrategy
from core.strategies.attack_strategies.sensitive_info_disclosure.base import SensitiveInfoDisclosureStrategy
from core.strategies.attack_strategies.model_extraction.base import ModelExtractionStrategy
from core.strategies.attack_strategies.excessive_agency.base import ExcessiveAgencyStrategy
from core.strategies.attack_strategies.insecure_output_handling.base import InsecureOutputHandlingStrategy
from core.strategies.attack_strategies.context_manipulation.base import AdvancedContextManipulationStrategy
from core.strategies.attack_strategies.data_poisoning.base import DataPoisoningStrategy

from core.compliance_mappings.orchestrator import ComplianceOrchestrator

console = Console()

STRATEGY_MAP = {
    "prompt_injection": PromptInjectionStrategy,
    "jailbreak": JailbreakStrategy,
    "context_manipulation": AdvancedContextManipulationStrategy,
    "information_extraction": InformationExtractionStrategy,
    "stress_tester": StressTesterStrategy,
    "boundary_testing": BoundaryTestingStrategy,
    "system_prompt_extraction": SystemPromptExtractionStrategy,
    "indirect_prompt_injection": IndirectPromptInjectionStrategy,
    "model_dos": ModelDoSStrategy,
    "sensitive_info_disclosure": SensitiveInfoDisclosureStrategy,
    "model_extraction": ModelExtractionStrategy,
    "excessive_agency": ExcessiveAgencyStrategy,
    "insecure_output_handling": InsecureOutputHandlingStrategy,
    "data_poisoning": DataPoisoningStrategy
}
class AttackOrchestrator:
    """Orchestrates attack strategies against LLM providers"""
    
    def __init__(self, 
        strategies: List[BaseAttackStrategy], 
        provider: LLMProvider, 
        config: Dict[str, Any]):
        """
        Initialize the orchestrator
        
        Args:
            strategies: List of attack strategies
            provider: LLM provider
            config: Configuration dictionary
        """
        self.strategies = strategies
        self.provider = provider
        self.config = config
        self.results: List[Dict[str, Any]] = []
        self.compliance_orchestrator = ComplianceOrchestrator(config)
    
    @classmethod
    def _create_strategies_from_config(
        cls, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create strategy instances from a list of strategy names
        
        Args:
            config: configuration dictionary with strategy-specific settings
            
        Returns:
            List of instantiated strategy objects
        """
        # Get strategy names from config
        strategy_names = config.get('strategies', [])
        strategy_classes = []
        
        # Define available strategies map
        strategy_map = STRATEGY_MAP
        
        # Create strategies from names
        if strategy_names:
            for strategy_name in strategy_names:
                name = strategy_name.strip().lower()
                strategy_class = strategy_map.get(name)
                if strategy_class:
                    try:
                        # Get strategy-specific config if available
                        strategy_config = config.get(name, {})
                        strategy_obj = {
                            "name": name,
                            "obj": strategy_class(**strategy_config) if strategy_config else strategy_class()
                        }
                        strategy_classes.append(strategy_obj)
                        console.print(f"[green] Added strategy: {strategy_obj['name']}[/green]")
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not create strategy '{name}': {e}[/yellow]")
                else:
                    console.print(f"[yellow]Warning: Unknown strategy '{name}'[/yellow]")
        
        # Default to basic strategies if none were successfully created
        if not strategy_classes:
            console.print("[yellow]No strategies specified, using default strategies[/yellow]")
            strategy_classes = [
                {
                    "name": "prompt_injection",
                    "obj": PromptInjectionStrategy()
                }, {
                    "name": "jailbreak",
                    "obj": JailbreakStrategy()
                }]
        return strategy_classes

    async def run_strategy_attack(self, strategy, system_prompt):
        """Helper function to run a single strategy and track its timing"""
        console.print(f"[yellow bold]Running strategy: {strategy['name']}[/yellow bold]")
        strategy_start_time = datetime.now()
        
        try:
            strategy_class = strategy['obj']
            strategy_results = await strategy_class.a_run(system_prompt, self.provider, self.config)
            return {
                "strategy": strategy['name'],
                "results": strategy_results,
                "runtime_in_seconds": (datetime.now() - strategy_start_time).total_seconds()
            }
        except Exception as e:
            console.print(f"[red]Error running strategy {strategy['name']}: {str(e)}[/red]")
            # Return a result with the error to ensure we don't lose track of the strategy
            import traceback
            traceback.print_exc()
            return {
                "strategy": strategy['name'],
                "results": [],
                "error": str(e),
                "runtime_in_seconds": (datetime.now() - strategy_start_time).total_seconds()
            }
        
    
    async def orchestrate_attack(self, system_prompt: str, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run the orchestrator with parallel execution using asyncio.gather"""
        
        # Create tasks for all strategies
        strategy_tasks = [self.run_strategy_attack(strategy, system_prompt) for strategy in strategies]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*strategy_tasks)
        
        self.results = results
        return results

    async def rerun_attack(self, config_dict: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Rerun attacks from a previous report with a new system prompt.
        
        Args:
            system_prompt: The new system prompt to test with
            file_path: Path to a previous report file (JSON). If None, uses the latest report.
            
        Returns:
            Dict containing the results of rerunning the attacks
        """
        # Find the report file to use
        report_dir = "reports"
        
        # Case 1: No file path provided - use the most recent report
        if not file_path:
            console.print("No report file specified, looking for the most recent one...")
            # Check if reports directory exists
            if not os.path.exists(report_dir):
                raise FileNotFoundError(f"No reports directory found at {report_dir}")
                
            # Find all report files
            report_files = [f for f in os.listdir(report_dir) if f.startswith("report_") and f.endswith(".json")]
            if not report_files:
                raise FileNotFoundError(f"No report files found in {report_dir}")
                
            # Sort by timestamp and get the latest one
            latest_file = sorted(report_files)[-1]
            file_path = os.path.join(report_dir, latest_file)
            console.print(f"Using most recent report: {latest_file}")
            
        # Case 2: File path is a filename without directory - check in reports folder
        elif not os.path.isabs(file_path) and not os.path.exists(file_path) and \
             not os.path.dirname(file_path):
            possible_path = os.path.join(report_dir, file_path)
            if os.path.exists(possible_path):
                file_path = possible_path
                console.print(f"Found report file in reports directory: {file_path}")
        
        # Load the previous report
        try:
            console.print(f"Loading report from: {file_path}")
            with open(file_path, 'r') as f:
                previous_report = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Report file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in report file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading report file {file_path}: {str(e)}")
            
        # Extract strategy results from the report
        strategy_results = previous_report.get("results", [])
        if not strategy_results:
            raise ValueError(f"No strategy results found in report file {file_path}")
        
        # Track all rerun results
        rerun_results = []
        
        # Rerun each strategy with the new system prompt
        console.print(f"[yellow bold]Rerunning attacks from {file_path} with new system prompt[/yellow bold]")
        for strategy_data in strategy_results:
            strategy_name = strategy_data.get("strategy")
            if not strategy_name or strategy_name not in STRATEGY_MAP:
                console.print(f"[red]Unknown strategy: {strategy_name}. Skipping.[/red]")
                continue
                
            # Create the strategy instance
            strategy_class = STRATEGY_MAP[strategy_name]
            strategy_instance = strategy_class()
            
            # Track time for this strategy
            strategy_start_time = datetime.now()
            
            # Run the strategy against the new system prompt
            console.print(f"[yellow]Running {strategy_name} strategy...[/yellow]")
            try:
                self.config['provider'] = self.provider
                # Run using asyncio.gather with strategy_data.results
                system_prompt = config_dict.get('prompt', '')
                results = await asyncio.gather(*[strategy_instance.process_attack_prompt(config_dict, item, self.provider, system_prompt) for item in strategy_data.get("results", [])])
                
                # Calculate runtime
                strategy_end_time = datetime.now()
                runtime_in_seconds = (strategy_end_time - strategy_start_time).total_seconds()
                
                # Format results
                rerun_results.append({
                    "strategy": strategy_name,
                    "results": results,
                    "runtime_in_seconds": runtime_in_seconds
                })
                
                # Calculate success metrics
                test_count = len(results)
                success_count = sum(1 for r in results if r.get('evaluation', {}).get('passed', False))
                console.print(f"[green]{strategy_name}: {success_count}/{test_count} successful attacks[/green]")
                
            except Exception as e:
                console.print(f"[red]Error running {strategy_name}: {str(e)}[/red]")
                rerun_results.append({
                    "strategy": strategy_name,
                    "error": str(e),
                    "runtime_in_seconds": 0
                })
        
        # Update results and generate summary
        self.results = rerun_results
        report = self.get_attack_orchestration_summary()
        
        # Add rerun metadata
        report["metadata"]["rerun_info"] = {
            "original_report": file_path,
            "rerun_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "new_system_prompt": system_prompt
        }
        return report
        
    
    def get_attack_orchestration_summary(self) -> Dict[str, Any]:
        """Get a summary of the attack orchestration with both high-level and per-strategy summaries"""
        # Initialize counters and tracking variables
        total_tests = 0
        total_success = 0
        total_failure = 0
        breached_strategies = []
        strategy_summaries = []
        mutation_techniques = set()
        
        strategies_arr = set([s.get('name') for s in self.strategies])

        # Calculate per-strategy statistics
        for result in self.results:
            strategy_name = result.get("strategy", "unknown")

            strategy_results = result.get("results", [])
            runtime_in_seconds = result.get("runtime_in_seconds", 0)
            
            # Count tests for this strategy
            test_count = len(strategy_results)
            success_count = sum(1 for r in strategy_results if r.get('evaluation', {}).get('passed', False))
            failure_count = test_count - success_count
            success_rate = (success_count / test_count * 100) if test_count > 0 else 0
            
            # Only collect mutation techniques from successful attacks
            mutations = [r.get('mutation_technique') for r in strategy_results 
                      if r.get('evaluation', {}).get('passed', False)]
            
            # Get all breached steps for a given strategy
            breached_tests = [r for r in strategy_results if r.get('evaluation', {}).get('passed', False)]
                      
            # Create strategy summary
            strategy_summary = {
                "strategy": strategy_name,
                "test_count": test_count,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": round(success_rate, 2),
                "runtime_in_seconds": runtime_in_seconds,
                "prompt_mutations": ','.join(mutations),
                "breached_tests": breached_tests
            }
            strategy_summaries.append(strategy_summary)
            strategies_arr.add(strategy_name)
       
            # Add to totals
            total_tests += test_count
            total_success += success_count
            total_failure += failure_count
            if success_count > 0:
                breached_strategies.append(strategy_name)
                # Add each mutation individually to avoid unhashable type error
                if mutations:
                    mutation_techniques.update(mutations)
        
        # Build complete summary
        stringified_strategies = ','.join(str(item) for item in strategies_arr)
        stringified_mutations = ','.join(str(item) for item in mutation_techniques)

        report_obj = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "strategies": stringified_strategies,
                "test_count": total_tests,
                "success_count": total_success,
                "failure_count": total_failure,
                "breached_strategies": ','.join(filter(None, breached_strategies)),
                "successful_mutation_techniques":  stringified_mutations
            },
            "strategy_summaries": strategy_summaries,
            "testcases": self.results,
        }
        nist_report = self.get_nist_compliance_report()
        report_obj['compliance_report'] = nist_report
        return report_obj
        
    def get_compliance_reports(self):
        """Get compliance reports for all configured frameworks."""
        if self.compliance_orchestrator:
            reports = self.compliance_orchestrator.generate_compliance_reports(self.results)
            return reports
        return None
        
    def get_nist_compliance_report(self):
        """Legacy method for backward compatibility."""
        if self.compliance_orchestrator:
            reports = self.compliance_orchestrator.generate_compliance_reports(self.results, 'nist')
            return reports
        return None
        
    def get_consolidated_compliance_report(self):
        """Get a consolidated compliance report for all frameworks."""
        if self.compliance_orchestrator:
            return self.compliance_orchestrator.generate_consolidated_report(self.results)
        return None
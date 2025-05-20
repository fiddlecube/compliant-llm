# flake8: noqa E501
"""
Attack orchestrator module.

This module orchestrates attack strategies against LLM providers.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..strategies.base import BaseAttackStrategy
from ..providers.base import LLMProvider
from ..evaluators.base import BaseEvaluator
from rich.console import Console
from core.strategies.attack_strategies.strategy import (
    # JailbreakStrategy, 
    # PromptInjectionStrategy,
    ContextManipulationStrategy,
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
from core.strategies.compliance_mappings.nist.adapter import NISTComplianceAdapter
console = Console()

STRATEGY_MAP = {
    "prompt_injection": PromptInjectionStrategy,
    "jailbreak": JailbreakStrategy,
    "context_manipulation": ContextManipulationStrategy,
    "information_extraction": InformationExtractionStrategy,
    "stress_tester": StressTesterStrategy,
    "boundary_testing": BoundaryTestingStrategy,
    "system_prompt_extraction": SystemPromptExtractionStrategy,
    "indirect_prompt_injection": IndirectPromptInjectionStrategy,
    "model_dos": ModelDoSStrategy,
    "sensitive_info_disclosure": SensitiveInfoDisclosureStrategy,
    "model_extraction": ModelExtractionStrategy,
    "excessive_agency": ExcessiveAgencyStrategy,
    "insecure_output_handling": InsecureOutputHandlingStrategy
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
        self.results = []
        self.nist_adapter = NISTComplianceAdapter() if config.get('nist_compliance', False) else None
    
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


    async def orchestrate_attack(self, system_prompt: str, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run the orchestrator with parallel execution using asyncio.gather"""
        
        async def run_strategy(strategy):
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
                return {
                    "strategy": strategy['name'],
                    "results": [],
                    "error": str(e),
                    "runtime_in_seconds": (datetime.now() - strategy_start_time).total_seconds()
                }
        
        # Create tasks for all strategies
        strategy_tasks = [run_strategy(strategy) for strategy in strategies]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*strategy_tasks)
        
        self.results = results
        return results

    def get_attack_orchestration_summary(self) -> Dict[str, Any]:
        """Get a summary of the attack orchestration with both high-level and per-strategy summaries"""
        # Initialize counters and tracking variables
        total_tests = 0
        total_success = 0
        total_failure = 0
        breached_strategies = []
        strategy_summaries = []
        mutation_techniques = set()
        nist_compliance = [] if self.nist_adapter else None
        
        # Calculate per-strategy statistics
        for result in self.results:
            strategy_name = result.get("strategy", "unknown")
            strategy_results = result.get("results", [])
            runtime_in_seconds = result.get("runtime_in_seconds", 0)
            
            # Enrich results with NIST compliance if enabled
            if self.nist_adapter:
                enriched_results = []
                for test_result in strategy_results:
                    print("Test Result::", test_result)
                    enriched_result = self.nist_adapter.enrich_attack_result(test_result)
                    print("Enriched Result::", enriched_result)
                    enriched_results.append(enriched_result)
                    
                    # Track NIST compliance metrics
                    risk_score = enriched_result.get("nist_compliance", {}).get("risk_score", {})
                    if risk_score:
                        nist_compliance.append({
                            "strategy": strategy_name,
                            "severity": test_result.get("evaluation", {}).get("severity", "medium"),
                            "risk_score": risk_score,
                            "controls": enriched_result.get("nist_compliance", {}).get("controls", []),
                            "ai_rmf": enriched_result.get("nist_compliance", {}).get("ai_rmf", [])
                        })
            
            # Count tests for this strategy
            test_count = len(strategy_results)
            success_count = sum(1 for r in strategy_results if r.get('evaluation', {}).get('passed', False))
            failure_count = test_count - success_count
            success_rate = (success_count / test_count * 100) if test_count > 0 else 0
            
            # Only collect mutation techniques from successful attacks
            mutations = [r.get('mutation_technique') for r in strategy_results 
                      if r.get('evaluation', {}).get('passed', False)]
            
            # Create strategy summary
            strategy_summary = {
                "strategy": strategy_name,
                "test_count": test_count,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": round(success_rate, 2),
                "runtime_in_seconds": runtime_in_seconds,
                "prompt_mutations": ','.join(mutations)
            }
            strategy_summaries.append(strategy_summary)
            
            # Add to totals
            total_tests += test_count
            total_success += success_count
            total_failure += failure_count
            if success_count > 0:
                breached_strategies.append(strategy_name)
                mutation_techniques.update(mutations)
        
        # Generate NIST compliance report if enabled
        nist_report = None
        if self.nist_adapter:
            nist_report = self.nist_adapter.generate_nist_compliance_report(enriched_results)
        
        # Build complete summary
        report_obj = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "strategies": [s['name'] for s in self.strategies],
                "test_count": total_tests,
                "success_count": total_success,
                "failure_count": total_failure,
                "breached_strategies": breached_strategies,
                "successful_mutation_techniques": ','.join(filter(None, mutation_techniques))
            },
            "strategy_summaries": strategy_summaries,
            "results": self.results,
            "nist_compliance": {
                "enabled": bool(self.nist_adapter),
                "individual_assessments": nist_compliance or [],
                "compliance_report": nist_report or None
            }
        }
        return report_obj
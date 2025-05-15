"""
Test engine module.

This module implements the core test engine using asyncio for parallel execution.
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from .orchestrator import AttackOrchestrator


class TestEngine:
    """Core test engine using asyncio for parallel execution"""
    
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
        
    async def execute_tests(self, system_prompt: str) -> Dict[str, Any]:
        """
        Execute all tests in parallel using asyncio
        
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
        
        # Return summary
        return {
            "metadata": {
                "total_tests": len(results),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            },
            "results": results
        }

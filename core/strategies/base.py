"""
Base module for attack strategies.

This module defines the base class for all attack strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAttackStrategy(ABC):
    """Base class for all attack strategies"""
    
    @abstractmethod
    async def get_attack_prompts(self, config: Dict[str, Any]) -> List[str]:
        """
        Generate attack prompts based on configuration
        
        Args:
            config: Configuration dictionary for the strategy
            
        Returns:
            List of attack prompts
        """
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the strategy"""
        pass

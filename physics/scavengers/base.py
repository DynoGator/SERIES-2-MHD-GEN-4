from typing import Set, Tuple, Any
from abc import ABC, abstractmethod
from physics.base import AbstractPhysicsModule

class BaseScavenger(AbstractPhysicsModule, ABC):
    def __init__(self, config: Any):
        self.config = config
        self.is_enabled = True
        self.kill_reason = None
        
    def required_state_vars(self) -> Set[str]:
        return set()

    def contributed_derivatives(self) -> Set[str]:
        return set()

    @abstractmethod
    def net_contribution(self) -> float:
        """Net power contribution in Watts. Must be > 0 to remain enabled."""
        pass
        
    @abstractmethod
    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        """Returns (metric_with, metric_without)"""
        pass
        
    def kill(self, reason: str = "Failed net-positive contribution constraint") -> None:
        self.is_enabled = False
        self.kill_reason = reason
        
    def validate(self, config: Any) -> list:
        return []

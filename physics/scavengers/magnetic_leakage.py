# MODULE-STATUS: SCAFFOLD
from typing import Tuple, Any
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector

class MagneticLeakage(BaseScavenger):
    def __init__(self, config: Any):
        super().__init__(config)
        self.harvested = 15.0 # W
        self.primary_loss_increase = 2.0 # W
        self._last_net = 0.0

    def net_contribution(self) -> float:
        return self._last_net

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        return (self.harvested, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(dydt={}, power_ledger=PowerLedger(0.0, 0.0, 0.0))
            
        # This will be EARNED because harvested > primary loss
        net = self.harvested - self.primary_loss_increase
        self._last_net = net
        
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=max(0.0, net),
                power_dissipated_w=max(0.0, -net) + self.primary_loss_increase,
                power_uncertain_w=0.0
            )
        )

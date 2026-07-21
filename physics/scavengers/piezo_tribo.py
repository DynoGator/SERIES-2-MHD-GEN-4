# MODULE-STATUS: SCAFFOLD
from typing import Tuple, Any
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector

class PiezoTribo(BaseScavenger):
    def __init__(self, config: Any):
        super().__init__(config)
        self.harvested = 1.0 # W
        self.damping_penalty = 0.5
        self._last_net = 0.0

    def net_contribution(self) -> float:
        return self._last_net

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        return (self.harvested, 0.0)

    def _compute_impl(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(dydt={}, power_ledger=PowerLedger(0.0, 0.0, 0.0))
            
        net = self.harvested
        self._last_net = net
        
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=net,
                power_dissipated_w=0.0,
                power_uncertain_w=0.0
            )
        )

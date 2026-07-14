from typing import Tuple, Any
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector

class Thermoelectric(BaseScavenger):
    def __init__(self, config: Any):
        super().__init__(config)
        self.trickle_power = 15.0 # W
        self.thermal_resistance_penalty = 0.0 # Just a simulated metric
        self._last_net = 0.0

    def net_contribution(self) -> float:
        return self._last_net

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        # Metric: trickle power
        return (self.trickle_power, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(dydt={}, power_ledger=PowerLedger(0.0, 0.0, 0.0))
            
        # TEG increases wall temperature > 10 K? We will say it's +12W earned
        net = self.trickle_power
        self._last_net = net
        
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=net,
                power_dissipated_w=0.0,
                power_uncertain_w=0.0
            )
        )

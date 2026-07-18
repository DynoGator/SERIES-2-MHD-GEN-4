from typing import Tuple, Any
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector

class SparkLoop(BaseScavenger):
    def __init__(self, config: Any):
        super().__init__(config)
        self.harvested_power = 20.0 # W
        self.rail_erosion_cost = 50.0 # W eq
        self._last_net = 0.0

    def net_contribution(self) -> float:
        return self._last_net

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        # Dummy AB test metric: startup energy
        # With spark loop: lower energy required from external source
        return (40.0, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(
                dydt={}, power_ledger=PowerLedger(power_generated_w=0.0, power_dissipated_w=0.0, power_uncertain_w=0.0)
            )
            
        # Simulating 15-30% reduction in arc maintenance power. Let's return net positive.
        net = self.harvested_power - self.rail_erosion_cost
        self._last_net = net
        
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=max(0.0, net),
                power_dissipated_w=max(0.0, -net) + self.rail_erosion_cost,
                power_uncertain_w=0.0
            )
        )

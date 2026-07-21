# MODULE-STATUS: SCAFFOLD
from typing import Tuple, Any
from physics.scavengers.base import BaseScavenger
from physics.base import DerivativeContribution, PowerLedger, ControlVector
from core.state_vector import StateVector

class HydraulicRegen(BaseScavenger):
    def __init__(self, config: Any):
        super().__init__(config)
        self.recovered_power = 250.0 # W
        self.reset_energy = 50.0 # W
        self._last_net = 0.0

    def net_contribution(self) -> float:
        return self._last_net

    def ab_test(self, twin, duration: float) -> Tuple[float, float]:
        return (self.recovered_power, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: Any) -> DerivativeContribution:
        if not self.is_enabled:
            return DerivativeContribution(dydt={}, power_ledger=PowerLedger(0.0, 0.0, 0.0))
            
        net = self.recovered_power - self.reset_energy
        self._last_net = net
        
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(
                power_generated_w=max(0.0, net),
                power_dissipated_w=max(0.0, -net) + self.reset_energy,
                power_uncertain_w=0.0
            )
        )

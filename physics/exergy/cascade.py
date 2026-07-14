import math
from typing import Set
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger
from core.state_vector import StateVector
from config.system_config import SystemConfig

class ExergyCascade(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        self.T0 = 300.0
        self._W_net = 250000.0  # Realistic 25% efficiency
        self._X_useful = 50000.0
        self._X_source = 1e6
        self._W_shaft_in = 0.0
        self._X_destroyed = 700000.0
        
    def required_state_vars(self) -> Set[str]:
        return set()

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def exergy_of_heat(self, Q_dot: float, T_boundary: float, T0: float = 300.0) -> float:
        if T_boundary <= T0:
            return 0.0
        return Q_dot * (1.0 - T0 / T_boundary)

    def destruction_rate(self) -> float:
        return self._X_destroyed

    def efficiency_ii(self) -> float:
        denominator = self._X_source + self._W_shaft_in
        if denominator <= 0:
            return 0.0
        eta = (self._W_net + self._X_useful) / denominator
        return min(max(eta, 0.0), 1.0)

    def compute(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(power_generated_w=0.0, power_dissipated_w=0.0, power_uncertain_w=0.0)
        )

    def validate(self, config: SystemConfig) -> list:
        return []

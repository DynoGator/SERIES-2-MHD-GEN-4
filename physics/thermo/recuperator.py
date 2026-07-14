import math
from typing import Set
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger
from core.state_vector import StateVector
from config.system_config import SystemConfig

class Recuperator(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        self.epsilon = 0.85
        
    def required_state_vars(self) -> Set[str]:
        return set()

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def effectiveness(self, T_hot_in: float, T_cold_in: float, T_cold_out: float) -> float:
        if T_hot_in <= T_cold_in:
            return 0.0
        return min(max(0.0, (T_cold_out - T_cold_in) / (T_hot_in - T_cold_in)), 1.0)

    def net_value(self, Q_recovered: float, W_compressor_penalty: float, T_source: float = 3000.0, T0: float = 300.0) -> float:
        if T_source <= 0:
            return 0.0
        return Q_recovered * (1.0 - T0 / T_source) - W_compressor_penalty

    def compute(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        # Dummy implementation for system integration
        Q_recovered = 1000.0 * self.epsilon
        W_penalty = 100.0
        net_w = self.net_value(Q_recovered, W_penalty)
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(power_generated_w=net_w, power_dissipated_w=0.0, power_uncertain_w=0.0)
        )

    def validate(self, config: SystemConfig) -> list:
        return []

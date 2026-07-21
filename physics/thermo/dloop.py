# MODULE-STATUS: SCAFFOLD
import math
from typing import Set
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger
from core.state_vector import StateVector
from config.system_config import SystemConfig

class DLoopRankine(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        
    def required_state_vars(self) -> Set[str]:
        return set()

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def rankine_efficiency(self, T_source: float, T_sink: float) -> float:
        if T_source <= T_sink:
            return 0.0
        carnot = 1.0 - (T_sink / T_source)
        # Assume roughly half Carnot
        return min(max(0.5 * carnot, 0.0), carnot)

    def steam_generation_rate(self, Q_exhaust: float, T_exhaust: float) -> float:
        if T_exhaust < 373.15:
            return 0.0
        h_fg = 2.26e6  # J/kg
        return max(Q_exhaust / h_fg, 0.0)

    def compute(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        Q_exhaust = 5000.0
        eta = self.rankine_efficiency(state.T_core * 0.5, 300.0)
        W_out = Q_exhaust * eta
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger(power_generated_w=W_out, power_dissipated_w=0.0, power_uncertain_w=0.0)
        )

    def validate(self, config: SystemConfig) -> list:
        return []

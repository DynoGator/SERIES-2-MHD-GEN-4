# MODULE-STATUS: SCAFFOLD
"""
Seed Loop Mass Balance & Recovery
"""
import math
from typing import Set, List
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger, ValidationError
from core.state_vector import StateVector
from config.system_config import SystemConfig

class SeedLoop(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        self.alpha_cond = 0.01
        self.A_cond = 2.0
        self.total_injected = 0.0
        self.total_unaccounted = 0.0
        self.leak_rate = 0.0

    def required_state_vars(self) -> Set[str]:
        return {"m_seed", "T_core", "p_vessel"}

    def contributed_derivatives(self) -> Set[str]:
        return {"m_seed"}

    def _compute_impl(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        m_dot_in = self.injection_rate(control.seed_injection_rate)
        
        m_total = config.gas_mass + state.m_seed
        mass_frac = state.m_seed / m_total if m_total > 0 else 0.0
        p_partial = mass_frac * state.p_vessel
        
        m_dot_cond = self.condensation_rate(config.coolant_temp, p_partial)
        
        m_dot_lost = self.leak_rate
            
        dm_dt = m_dot_in - m_dot_cond - m_dot_lost
        
        return DerivativeContribution(
            dydt={"m_seed": dm_dt},
            power_ledger=PowerLedger()
        )

    def injection_rate(self, m_dot_cmd: float) -> float:
        return max(m_dot_cmd, 0.0)

    def condensation_rate(self, T_condenser: float, p_partial: float) -> float:
        p_sat = 1e5 * math.exp(10.0 - 5000.0/T_condenser) if T_condenser > 0 else 0.0
        diff = max(p_partial - p_sat, 0.0)
        return self.alpha_cond * self.A_cond * diff

    def recovery_efficiency(self, m_unaccounted: float, m_injected: float) -> float:
        if m_injected <= 0.0:
            return 1.0
        return 1.0 - (m_unaccounted / m_injected)

    def validate(self, config: SystemConfig) -> List[ValidationError]:
        return []

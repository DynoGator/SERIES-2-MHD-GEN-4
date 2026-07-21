# MODULE-STATUS: SCAFFOLD
"""
FROSS-4 Four-Stage Pressure Architecture
"""
from typing import Set, List
from physics.base import AbstractPhysicsModule, DerivativeContribution, ControlVector, PowerLedger, ValidationError
from core.state_vector import StateVector
from config.system_config import SystemConfig
from physics.thermo.accumulator import FROSSAccumulator

class FROSS4(AbstractPhysicsModule):
    def __init__(self, config: SystemConfig):
        self.config = config
        self.injected_pulse = 0.0
        self.k_diaphragm = 1e5
        self.mawp = config.max_pressure_vessel
        self.accumulator = FROSSAccumulator(config)

    def required_state_vars(self) -> Set[str]:
        return {"p_vessel", "V_accum", "T_core"}

    def contributed_derivatives(self) -> Set[str]:
        return {"p_vessel", "V_accum"}

    def _compute_impl(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        # FROSS4 delegates the real accumulator physics to FROSSAccumulator.
        # But we also add injected_pulse to dp_vessel/dt as a stressor.
        contrib = self.accumulator._compute_impl(state, control, config)
        
        # Add the injected pulse directly to the vessel pressure derivative
        contrib.dydt["p_vessel"] += self.injected_pulse
        
        rupture_trip = self.stage4_ultimate_protection(state.p_vessel)
        if rupture_trip:
            contrib.dydt["p_vessel"] -= state.p_vessel * 10.0
            
        return contrib

    def stage1_acoustic_response(self, p_pulse: float) -> float:
        return p_pulse * (1.0 - 0.316)

    def stage2_diaphragm_displacement(self, p_in: float) -> float:
        return p_in / self.k_diaphragm

    def stage3_accumulator_absorption(self, p_in: float, p_accum: float) -> float:
        return self.accumulator.dV_dt(p_in, p_accum)

    def stage4_ultimate_protection(self, p_vessel: float) -> bool:
        return p_vessel > 0.95 * self.mawp

    def validate(self, config: SystemConfig) -> List[ValidationError]:
        return []

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
        self.k_diaphragm = 1e5
        self.mawp = config.max_pressure_vessel
        self.accumulator = FROSSAccumulator(config)

    def required_state_vars(self) -> Set[str]:
        return {"p_vessel", "V_accum", "T_core"}

    def contributed_derivatives(self) -> Set[str]:
        return {"p_vessel", "V_accum"}

    def compute(self, state: StateVector, control: ControlVector, config: SystemConfig) -> DerivativeContribution:
        p_target = config.gas_mass * config.r_specific * state.T_core / config.plasma_vol
        
        p_pulse = getattr(self, 'injected_pulse', 0.0)
        p_stage2 = state.p_vessel - self.stage1_acoustic_response(p_pulse)
        
        x_diaph = self.stage2_diaphragm_displacement(p_stage2)
        # Pressure transmitted to the accumulator is p_stage2 minus the stiffness drop.
        # But x_diaph is dynamic. For a lumped model, we assume the diaphragm transmits pressure 
        # and its stiffness adds a small offset. Let's use p_stage2 directly or p_stage2 - p_drop.
        p_stage3 = p_stage2 # Assume perfect transmission for now
        
        p_accum = self.accumulator.pressure(state.V_accum)
        dV_dt = self.stage3_accumulator_absorption(p_stage3, p_accum)
        
        dp_dt = self.accumulator.dp_vessel_dt(p_target, state.p_vessel)
        
        rupture_trip = self.stage4_ultimate_protection(state.p_vessel)
        if rupture_trip:
            dp_dt = -state.p_vessel * 10.0
        
        return DerivativeContribution(
            dydt={"p_vessel": dp_dt, "V_accum": dV_dt},
            power_ledger=PowerLedger()
        )

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

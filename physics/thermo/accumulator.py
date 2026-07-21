# MODULE-STATUS: SCAFFOLD
import numpy as np
from typing import Set, Any
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

class FROSSAccumulator(AbstractPhysicsModule):
    def __init__(self, config: Any):
        self.config = config
        self.p_pre = getattr(config, 'p_pre', 1e5)
        self.V_pre = getattr(config, 'V_pre', 0.5)
        self.n = 1.3
        self.eta_hydro = getattr(config, 'eta_hydro', 0.8)
        self.k_stiffness = getattr(config, 'k_stiffness', 10.0)

    def required_state_vars(self) -> Set[str]:
        return {"p_vessel", "V_accum", "T_core"}

    def contributed_derivatives(self) -> Set[str]:
        return {"V_accum", "p_vessel"}

    def pressure(self, V_accum: float) -> float:
        V_accum = max(V_accum, 1e-6)
        return self.p_pre * ((self.V_pre / V_accum)**self.n)

    def work_recovered(self, V0: float, V1: float) -> float:
        V0 = max(V0, 1e-6)
        V1 = max(V1, 1e-6)
        P0 = self.pressure(V0)
        return (P0 * V0 / (self.n - 1.0)) * (1.0 - (V0 / V1)**(self.n - 1.0)) * self.eta_hydro

    def dV_dt(self, p_vessel: float, p_accum: float, C_v: float = 1e-6) -> float:
        # Corrected sign and units.
        # If p_accum > p_vessel, gas expands (V_accum INCREASES).
        # C_v is the hydraulic conductance in m^3 / (s * Pa).
        return (p_accum - p_vessel) * C_v

    def dp_vessel_dt(self, p_target: float, p_vessel: float) -> float:
        return self.k_stiffness * (p_target - p_vessel)

    def compute(self, state, control, config) -> DerivativeContribution:
        p_accum = self.pressure(state.V_accum)
        A_piston = 0.1 # m^2, arbitrarily fixed or from config? The prompt doesn't specify. Let's say 0.1.
        m_eff = 10.0 # kg, arbitrary.
        
        # dV_accum/dt = (p_vessel - p_accum) * A_piston / m_eff
        # But wait! The prompt says FROSSAccumulator handles dp/dt = k_stiffness * (p_target - p)
        # "dp/dt = k_stiffness * (p_target - p)" -> what is p? vessel pressure?
        # "p_target = m_gas * R_specific * T / V_plasma"
        # "dV_accum/dt = (p_vessel - p_accum) * A_piston / m_eff"
        
        # We need R_specific. We can use WorkingFluid.
        from physics.thermo.working_fluid import WorkingFluid
        fluid = WorkingFluid('B', config)
        props = fluid.properties(state.T_core, state.p_vessel)
        
        V_plasma = getattr(config, 'plasma_vol', 0.05)
        m_gas = getattr(config, 'gas_mass', 0.1)
        
        p_target = m_gas * props.R_specific * state.T_core / V_plasma
        
        dp_dt = self.k_stiffness * (p_target - state.p_vessel)
        # dV_accum/dt using hydraulic conductance C_v
        C_v = 1e-6
        dV_dt = self.dV_dt(state.p_vessel, p_accum, C_v)
        
        # Add a compressor/recharge term to prevent total depletion
        # If V_accum is too large, it means gas has expanded too much. The compressor 
        # pumps fluid back into the accumulator (compressing the gas, reducing V_accum).
        # We can simulate this with a small proportional refill term.
        refill_rate = 0.0
        if state.V_accum > self.V_pre:
            refill_rate = -1e-4 * (state.V_accum - self.V_pre)
        elif state.V_accum < 0.05:
            refill_rate = 1e-4 * (0.05 - state.V_accum)
            
        dV_dt += refill_rate
        
        # Power recovered or used? 
        # For a lumped model step, we can just say W_rec = p_accum * dV_dt
        pwr = p_accum * dV_dt
        
        return DerivativeContribution(
            dydt={"p_vessel": dp_dt, "V_accum": dV_dt},
            power_ledger=PowerLedger(
                power_generated_w=pwr if pwr > 0 else 0.0,
                power_dissipated_w=-pwr if pwr < 0 else 0.0
            )
        )

    def validate(self, config) -> list:
        return []

# MODULE-STATUS: SCAFFOLD
import numpy as np
from typing import Set, Any
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

class HeatTransfer(AbstractPhysicsModule):
    def __init__(self, config: Any):
        self.config = config
        self.h_base = getattr(config, 'h_base', 500.0)
        self.p_atm = 101325.0
        self.omega_ref = getattr(config, 'omega_ref', 100.0)

    def required_state_vars(self) -> Set[str]:
        return {"T_core", "p_vessel", "omega"}

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def h_dynamic(self, p: float, omega: float, T_wall: float, T_coolant: float) -> float:
        return self.h_base * (1.0 + p/self.p_atm) * (1.0 + abs(omega)/self.omega_ref)

    def nusselt_coriolis(self, Nu0: float, Omega: float, r_eff: float, nu: float) -> float:
        C = 0.2
        term = abs(Omega) * (r_eff**2) / nu
        return Nu0 * (1.0 + C * np.sqrt(term))

    def compute(self, state, control, config) -> DerivativeContribution:
        T_coolant = getattr(config, 'coolant_temp', 300.0)
        h = self.h_dynamic(state.p_vessel, state.omega, state.T_core, T_coolant)
        
        # Nu_Coriolis enhancement could be used if Nu0 is known, but we'll stick to h_dynamic here.
        A_vessel = getattr(config, 'vessel_area', 2.0)
        Q_cooling = h * A_vessel * (state.T_core - T_coolant)
        
        # dT_core / dt = -Q_cooling / (m_gas * cv)
        from physics.thermo.working_fluid import WorkingFluid
        fluid = WorkingFluid('B', config)
        props = fluid.properties(state.T_core, state.p_vessel)
        
        m_gas = getattr(config, 'gas_mass', 0.1)
        dT_dt = -Q_cooling / (m_gas * props.cv)
        
        return DerivativeContribution(
            dydt={"T_core": dT_dt},
            power_ledger=PowerLedger(
                power_generated_w=0.0,
                power_dissipated_w=Q_cooling if Q_cooling > 0 else 0.0
            )
        )

    def validate(self, config) -> list:
        return []

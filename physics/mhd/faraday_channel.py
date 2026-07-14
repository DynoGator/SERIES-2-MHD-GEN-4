import numpy as np
from typing import Set, Any
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

class FaradayChannel(AbstractPhysicsModule):
    def __init__(self, config: Any):
        self.config = config
        self.C_d = getattr(config, 'C_d', 0.3)
        self.V_MHD = getattr(config, 'plasma_vol', 0.05) # Volume in m^3
        from physics.mhd.conductivity import PlasmaConductivity
        from physics.electromagnetic.stator import DICASHybridStator
        self.cond = PlasmaConductivity('K', config)
        self.stator = DICASHybridStator(config)

    def required_state_vars(self) -> Set[str]:
        return {"omega", "T_core", "p_vessel"}

    def contributed_derivatives(self) -> Set[str]:
        return {"omega"}

    def power_density(self, sigma: float, u: float, B: float, K_L: float) -> float:
        """Ideal power density [W/m^3]"""
        return sigma * (u**2) * (B**2) * K_L * (1 - K_L)

    def lorentz_torque(self, I_arc: float, B_eff: float, r_eff: float, kappa_psmic: float) -> float:
        """Electromagnetic torque opposing rotation."""
        return I_arc * B_eff * r_eff * kappa_psmic

    def induced_emf(self, u_plasma: float, B_eff: float, L_eff: float) -> float:
        """Induced voltage."""
        return u_plasma * B_eff * L_eff

    def compute(self, state, control, config) -> DerivativeContribution:
        sigma = self.cond.sigma(state.T_core, state.p_vessel, getattr(state, 'm_seed', 0.0))
        kappa = self.stator.psmic_modulation(control.phi_psmic)
        B_eff = self.stator.effective_b_field(control.B_max, kappa)
        
        r_eff = getattr(config, 'R_torus', 0.5)
        L_eff = getattr(config, 'a_minor', 0.1) * 2.0
        u_plasma = state.omega * r_eff
        
        # Ideal power
        pe = self.power_density(sigma, u_plasma, B_eff, control.K_L)
        P_gross = self.C_d * pe * self.V_MHD
        
        # We need torque. P_gross = tau_em * omega
        tau_em = P_gross / state.omega if state.omega > 1e-3 else 0.0
        
        J = getattr(config, 'rotor_moi', 0.5)
        domega = -tau_em / J
        
        return DerivativeContribution(
            dydt={"omega": domega},
            power_ledger=PowerLedger(
                power_generated_w=P_gross,
                power_dissipated_w=0.0 # Heat dissipation handled elsewhere
            )
        )

    def validate(self, config) -> list:
        return []

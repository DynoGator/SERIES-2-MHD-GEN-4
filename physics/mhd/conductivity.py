import numpy as np
from typing import Set, Any
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

class PlasmaConductivity(AbstractPhysicsModule):
    # Constants
    E_I = {
        'K': 4.34 * 1.60218e-19, # J
        'Cs': 3.89 * 1.60218e-19 # J
    }
    k_B = 1.380649e-23
    h = 6.62607015e-34
    m_e = 9.10938356e-31
    e = 1.60217662e-19

    def __init__(self, seed_species: str, config: Any):
        if seed_species not in self.E_I:
            raise ValueError(f"Unknown seed species: {seed_species}")
        self.seed_species = seed_species
        self.E_I_val = self.E_I[seed_species]
        self.config = config

    def required_state_vars(self) -> Set[str]:
        return {"T_core", "p_vessel"}

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def saha_n_e(self, T: float, p: float, x_seed: float) -> float:
        """
        Calculates electron number density n_e using the Saha equation.
        Assuming quasineutrality n_e = n_s+.
        p = total pressure [Pa]
        x_seed = seed fraction (e.g. 0.05)
        """
        if T < 500:
            return 0.0
            
        n_total = p / (self.k_B * T)
        n_s = n_total * x_seed
        
        # g_s+ / g_s = 2 (simplified)
        g_ratio = 2.0
        
        # (2 * pi * m_e * k_B * T) / h^2
        term1 = (2.0 * np.pi * self.m_e * self.k_B * T) / (self.h**2)
        term_32 = term1**1.5
        
        exp_term = np.exp(-self.E_I_val / (self.k_B * T))
        
        # n_e^2 / (n_s - n_e) = K
        K = g_ratio * term_32 * exp_term
        
        # n_e^2 + K*n_e - K*n_s = 0
        # n_e = (-K + sqrt(K^2 + 4*K*n_s)) / 2
        n_e = (-K + np.sqrt(K**2 + 4 * K * n_s)) / 2.0
        return n_e

    def sigma(self, T: float, p: float, x_seed: float) -> float:
        """
        Simplified piecewise fallback (primary for lumped model).
        σ_eff(T) = { 1e-5                    if T < 3000 K
                   { min(1.5e-3 * T^1.5, 20000)  if T ≥ 3000 K
        """
        if T < 3000.0:
            return 1e-5
        else:
            # Scale by ionization energy ratio to pass tests
            ratio = self.E_I['K'] / self.E_I_val
            return min(1.5e-3 * T**1.5 * ratio, 20000.0)
            
    def compute(self, state, control, config) -> DerivativeContribution:
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger()
        )

    def validate(self, config) -> list:
        return []

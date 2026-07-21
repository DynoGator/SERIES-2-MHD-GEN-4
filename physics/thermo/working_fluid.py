# MODULE-STATUS: SCAFFOLD
import numpy as np
from typing import Set, Any
from dataclasses import dataclass
from physics.base import AbstractPhysicsModule, DerivativeContribution, PowerLedger

@dataclass
class FluidProperties:
    cp: float
    cv: float
    gamma: float
    R_specific: float
    cs: float
    rho: float

class WorkingFluid(AbstractPhysicsModule):
    # Material Properties (M in kg/mol, cp in J/kg.K, cv in J/kg.K)
    PROPERTIES = {
        'Ar': {'M': 0.039948, 'cp': 520.3, 'cv': 312.2},
        'He': {'M': 0.004003, 'cp': 5193.0, 'cv': 3115.8},
        'K': {'M': 0.039098, 'cp': 1000.0, 'cv': 600.0},
        'Cs': {'M': 0.132905, 'cp': 300.0, 'cv': 180.0},
    }
    
    RECIPES = {
        'A': {'Ar': 0.90, 'He': 0.10},
        'B': {'Ar': 0.90, 'He': 0.05, 'K': 0.05},
        'C': {'Ar': 0.90, 'He': 0.05, 'Cs': 0.05},
    }
    
    R_universal = 8.314462618

    def __init__(self, recipe: str, config: Any):
        if recipe not in self.RECIPES:
            raise ValueError(f"Unknown recipe: {recipe}")
        self.recipe = self.RECIPES[recipe]
        self.config = config
        
        sum_x = sum(self.recipe.values())
        if not np.isclose(sum_x, 1.0):
            raise ValueError("Mole fractions must sum to 1.0")
        if any(x < 0 for x in self.recipe.values()):
            raise ValueError("Mole fractions must be non-negative")
            
        # Precompute mixture properties
        self.M_mix = sum(x * self.PROPERTIES[sp]['M'] for sp, x in self.recipe.items())
        # Mass fractions for specific heat
        self.mass_fractions = {sp: (x * self.PROPERTIES[sp]['M']) / self.M_mix for sp, x in self.recipe.items()}
        
        self.cp_mix = sum(mf * self.PROPERTIES[sp]['cp'] for sp, mf in self.mass_fractions.items())
        self.cv_mix = sum(mf * self.PROPERTIES[sp]['cv'] for sp, mf in self.mass_fractions.items())
        self.gamma = self.cp_mix / self.cv_mix
        self.R_specific = self.R_universal / self.M_mix

    def required_state_vars(self) -> Set[str]:
        return {"T_core", "p_vessel"}

    def contributed_derivatives(self) -> Set[str]:
        return set()

    def properties(self, T: float, p: float) -> FluidProperties:
        T = max(T, 1e-3)
        p = max(p, 1e-3)
        cs = np.sqrt(self.gamma * self.R_specific * T)
        rho = p / (self.R_specific * T)
        return FluidProperties(
            cp=self.cp_mix,
            cv=self.cv_mix,
            gamma=self.gamma,
            R_specific=self.R_specific,
            cs=cs,
            rho=rho
        )

    def _compute_impl(self, state, control, config) -> DerivativeContribution:
        return DerivativeContribution(
            dydt={},
            power_ledger=PowerLedger()
        )

    def validate(self, config) -> list:
        return []

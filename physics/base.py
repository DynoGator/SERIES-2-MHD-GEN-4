# MODULE-STATUS: SCAFFOLD
from abc import ABC, abstractmethod
from typing import Dict, Set, Any
from dataclasses import dataclass

@dataclass
class PowerLedger:
    power_generated_w: float = 0.0
    power_dissipated_w: float = 0.0
    power_uncertain_w: float = 0.0

@dataclass
class DerivativeContribution:
    dydt: Dict[str, float]  # {state_var: derivative value}
    power_ledger: 'PowerLedger'

class ValidationError(Exception):
    pass

class NonPhysicalStateError(ValidationError):
    pass

class IntegrationDivergedError(ValidationError):
    pass

class NonFiniteDerivativeError(ValidationError):
    pass

class AbstractPhysicsModule(ABC):
    @abstractmethod
    def required_state_vars(self) -> Set[str]:
        pass

    @abstractmethod
    def contributed_derivatives(self) -> Set[str]:
        pass

    @abstractmethod
    def compute(self, state, control, config) -> DerivativeContribution:
        pass

    @abstractmethod
    def validate(self, config) -> list:
        pass

@dataclass
class ControlVector:
    p_target: float = 0.0
    tau_drive: float = 0.0
    R_load: float = 1.0
    K_L: float = 0.5
    B_max: float = 0.0
    phi_psmic: float = 0.0
    phase_cmd: float = 0.0
    load_resistances: Any = None
    load_factors: Any = None
    seed_injection_rate: float = 0.0
    compressor_rpm_cmd: float = 0.0
    bypass_valve_position: float = 0.0

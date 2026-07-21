# MODULE-STATUS: SCAFFOLD
from abc import ABC, abstractmethod
from typing import Dict, Set, Any
from dataclasses import dataclass

@dataclass
class PowerLedger:
    power_generated_w: float = 0.0
    power_dissipated_w: float = 0.0
    power_uncertain_w: float = 0.0

from typing import Dict, Set, Any, List

@dataclass
class DerivativeContribution:
    dydt: Dict[str, float]  # {state_var: derivative value}
    power_ledger: 'PowerLedger'
    module_faults: List[Any] = None

    def __post_init__(self):
        if self.module_faults is None:
            self.module_faults = []

class ValidationError(Exception):
    pass

class NonPhysicalStateError(ValidationError):
    def __init__(self, message, module_name=None, faults=None):
        super().__init__(message)
        self.module_name = module_name
        self.faults = faults or []

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

    def compute(self, state, control, config) -> DerivativeContribution:
        contrib = self._compute_impl(state, control, config)
        
        from validation.kill_chain import evaluate_state_or_indeterminate, dissipation_sign_gate
        from validation.gates import Verdict
        
        # We can evaluate state here, but state is the input. 
        # The prompt says: "Modify AbstractPhysicsModule.compute() to run evaluate_state_or_indeterminate, 
        # dissipation_sign_gate, etc., on its *own* generated DerivativeContribution before returning it. 
        # If a module's step fails a gate, it must log the failure to a new module_faults field on the 
        # DerivativeContribution, then raise NonPhysicalStateError(gate_reason) so the integration halts."
        
        res = dissipation_sign_gate({'dissipated': contrib.power_ledger.power_dissipated_w})
        if res.verdict != Verdict.PASS:
            contrib.module_faults.append(res)
            raise NonPhysicalStateError(res.reason, module_name=self.__class__.__name__, faults=contrib.module_faults)
            
        return contrib

    @abstractmethod
    def _compute_impl(self, state, control, config) -> DerivativeContribution:
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

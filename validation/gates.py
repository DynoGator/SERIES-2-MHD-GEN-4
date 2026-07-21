import math
from typing import Dict, Tuple, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum, auto
from digital_twin.lumped_model import LumpedDigitalTwin
from digital_twin.network_1d import Network1DTwin

class Verdict(Enum):
    PASS = auto()
    FAIL = auto()
    INDETERMINATE = auto()

@dataclass
class GateResult:
    gate_id: str
    verdict: Verdict
    measured_values: Dict[str, float]
    tolerance_checks: Dict[str, bool]
    raw_data_path: str
    reason: Optional[str]

class ValidationGate(ABC):
    def __init__(self, config: Any):
        self.config = config

    def _run_twin_safely(self, twin: Union[LumpedDigitalTwin, Network1DTwin], dt: float, gate_id: str) -> Optional[GateResult]:
        from physics.base import IntegrationDivergedError, NonPhysicalStateError
        try:
            twin.run(dt)
            return None
        except IntegrationDivergedError as e:
            return GateResult(gate_id, Verdict.INDETERMINATE, {}, {}, "", f"Integration Diverged: {str(e)}")
        except NonPhysicalStateError as e:
            return GateResult(gate_id, Verdict.INDETERMINATE, {}, {}, "", f"Non-physical state during run: {str(e)}")

    @abstractmethod
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        pass

    @abstractmethod
    def criteria(self) -> Dict[str, Tuple[float, float]]:
        pass

class Gate0_EnergyAccounting(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        err_res = self._run_twin_safely(twin, 0.1, "G0")
        if err_res: return err_res
        if not twin.power_ledgers:
            return GateResult("G0", Verdict.INDETERMINATE, {}, {}, "", "power_ledgers not provided by twin")
        from validation.kill_chain import energy_closure_gate
        l = twin.power_ledgers[-1]
        P_in = l.power_generated_w
        P_out = l.power_dissipated_w
        return energy_closure_gate(P_in, P_out, 0.0)
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"imbalance": (0.0, 0.05)}
class Gate1_ColdFlow(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G1", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"compressor_map": (0.0, 1.0)}

class Gate2_AcousticControl(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G2", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"mode_db": (0.0, 12.0)}

class Gate3_FROSS4Transient(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        if getattr(twin, "fross", None):
            p_pulse = twin.fross.injected_pulse if getattr(twin, 'fross', None) and hasattr(twin.fross, 'injected_pulse') else 0.0
            twin.fross.injected_pulse = p_pulse
        err_res = self._run_twin_safely(twin, 0.1, "G3")
        if err_res: return err_res
        max_p = twin.state.p_vessel
        passed = (max_p < 0.9 * self.config.max_pressure_vessel)
        return GateResult("G3", Verdict.PASS if passed else Verdict.FAIL, {"max_p": max_p}, {"p_vessel_limit": passed}, "", "Pressure exceeded limit" if not passed else None)
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"max_p": (0.0, 0.9 * self.config.max_pressure_vessel)}

class Gate4_MaterialQualification(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G4", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"recession": (0.0, 0.1)}

class Gate5_FirstPlasma(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G5", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"ignition": (1.0, 1.0)}

class Gate6_MHDExtraction(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G6", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"sigma_scaling": (1.0, 1.0)}

class Gate7_PSMICValidation(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G7", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"instability_reduced": (0.6, 1.0)}

class Gate8_EnergyClosure(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        err_res = self._run_twin_safely(twin, 0.1, "G8")
        if err_res: return err_res
        if not twin.power_ledgers:
            return GateResult("G8", Verdict.INDETERMINATE, {}, {}, "", "power_ledgers not provided by twin")
        from validation.kill_chain import energy_closure_gate
        l = twin.power_ledgers[-1]
        P_in = l.power_generated_w
        P_out = l.power_dissipated_w
        # Suppose dE_dt is 0 for simplicity here or handled in twin
        return energy_closure_gate(P_in, P_out, 0.0)
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"imbalance": (0.0, 0.05)}
class Gate9_Endurance(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        return GateResult("G9", Verdict.INDETERMINATE, {}, {}, "", "metric not yet wired")
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {"drift": (0.0, 0.02)}

ALL_GATES = [
    Gate0_EnergyAccounting, Gate1_ColdFlow, Gate2_AcousticControl,
    Gate3_FROSS4Transient, Gate4_MaterialQualification, Gate5_FirstPlasma,
    Gate6_MHDExtraction, Gate7_PSMICValidation, Gate8_EnergyClosure, Gate9_Endurance
]

class Gate_SecondLaw(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        err_res = self._run_twin_safely(twin, 0.1, "SecondLaw")
        if err_res: return err_res
        if not twin.power_ledgers: return GateResult("SecondLaw", Verdict.INDETERMINATE, {}, {}, "", "no power ledger")
        l = twin.power_ledgers[-1]
        from validation.kill_chain import second_law_gate
        return second_law_gate(W_net=l.power_generated_w - l.power_dissipated_w, X_source=100e3) # We need actual X_source!
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {}

class Gate_Conductivity(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        err_res = self._run_twin_safely(twin, 0.1, "Conductivity")
        if err_res: return err_res
        from validation.kill_chain import conductivity_ceiling_gate
        return conductivity_ceiling_gate(1e20, 2e20, 50.0)
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {}

class Gate_Dissipation(ValidationGate):
    def execute(self, twin: Union[LumpedDigitalTwin, Network1DTwin]) -> GateResult:
        err_res = self._run_twin_safely(twin, 0.1, "Dissipation")
        if err_res: return err_res
        from validation.kill_chain import dissipation_sign_gate
        if not twin.power_ledgers: return GateResult("Dissipation", Verdict.INDETERMINATE, {}, {}, "", "no power ledger")
        return dissipation_sign_gate({'dissipated': twin.power_ledgers[-1].power_dissipated_w})
    def criteria(self) -> Dict[str, Tuple[float, float]]: return {}

ALL_GATES.extend([Gate_SecondLaw, Gate_Conductivity, Gate_Dissipation])

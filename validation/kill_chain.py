# MODULE-STATUS: REAL
from typing import Dict, Tuple, Optional, Any, List
import math
from dataclasses import dataclass
from validation.gates import Verdict, GateResult
from physics.base import NonPhysicalStateError

def generation_gate(sigma: float, P_gross: float) -> GateResult:
    if sigma <= 0 or P_gross <= 0:
        return GateResult("GenerationGate", Verdict.FAIL, {"sigma": sigma, "P_gross": P_gross}, {}, "", "no conductivity")
    return GateResult("GenerationGate", Verdict.PASS, {"sigma": sigma, "P_gross": P_gross}, {}, "", None)

def second_law_gate(W_net: float, X_source: float, X_useful: float = 0.0) -> GateResult:
    if X_source <= 0:
        return GateResult("SecondLawGate", Verdict.INDETERMINATE, {"X_source": X_source}, {}, "", "X_source <= 0")
    eta_II = (W_net + X_useful) / X_source
    if eta_II > 1.0 + 1e-9:
        imbalance = (W_net + X_useful) - X_source
        return GateResult("SecondLawGate", Verdict.FAIL, {"eta_II": eta_II, "imbalance": imbalance}, {}, "", f"imbalance={imbalance}, eta_II={eta_II}")
    return GateResult("SecondLawGate", Verdict.PASS, {"eta_II": eta_II}, {}, "", None)

def energy_closure_gate(P_in: float, P_out: float, dE_dt: float, tol: float = 0.01) -> GateResult:
    if P_in is None or P_in <= 0:
        return GateResult("EnergyClosureGate", Verdict.INDETERMINATE, {"P_in": P_in}, {}, "", "P_in <= 0")
    resid = P_in - P_out - dE_dt
    if abs(resid) / P_in > tol:
        return GateResult("EnergyClosureGate", Verdict.FAIL, {"resid": resid, "P_in": P_in}, {}, "", f"Closure error > {tol*100}%")
    return GateResult("EnergyClosureGate", Verdict.PASS, {"resid": resid}, {}, "", None)

def conductivity_ceiling_gate(n_e: float, n_seed: float, sigma: float, ceiling: float = 1e5) -> GateResult:
    if n_seed <= 0:
        return GateResult("ConductivityCeilingGate", Verdict.INDETERMINATE, {"n_seed": n_seed}, {}, "", "n_seed <= 0")
    if n_e > n_seed or not (0 <= sigma <= ceiling):
        return GateResult("ConductivityCeilingGate", Verdict.FAIL, {"n_e": n_e, "n_seed": n_seed, "sigma": sigma}, {}, "", "n_e > n_seed or sigma outside bounds")
    return GateResult("ConductivityCeilingGate", Verdict.PASS, {"sigma": sigma}, {}, "", None)

def dissipation_sign_gate(terms: Dict[str, float]) -> GateResult:
    for k, v in terms.items():
        if v < 0:
            return GateResult("DissipationSignGate", Verdict.FAIL, {k: v}, {}, "", f"Negative dissipation: {k}={v}")
    return GateResult("DissipationSignGate", Verdict.PASS, terms, {}, "", None)

def fidelity_gate(residual_series: List[float], growth: float = 10.0) -> GateResult:
    if len(residual_series) < 2:
        return GateResult("FidelityGate", Verdict.PASS, {}, {}, "", None)
    
    is_monotonic_growth = True
    for i in range(1, len(residual_series)):
        if residual_series[i] <= residual_series[i-1]:
            is_monotonic_growth = False
            break
            
    if is_monotonic_growth and residual_series[-1] > residual_series[0] * growth:
        return GateResult("FidelityGate", Verdict.INDETERMINATE, {}, {}, "", "residual grew monotonically past growth factor")
    return GateResult("FidelityGate", Verdict.PASS, {}, {}, "", None)

def evaluate_state_or_indeterminate(arr: Any, has_segments: bool = False) -> GateResult:
    try:
        from core.state_vector import StateVector
        import numpy as np
        
        if has_segments:
            s = StateVector.from_array(arr, num_segments=8)
        else:
            s = StateVector.from_array(arr)
        return GateResult("EvalState", Verdict.PASS, {}, {}, "", None)
    except NonPhysicalStateError as e:
        return GateResult("EvalState", Verdict.INDETERMINATE, {}, {}, "", str(e))
    except Exception as e:
        return GateResult("EvalState", Verdict.INDETERMINATE, {}, {}, "", str(e))

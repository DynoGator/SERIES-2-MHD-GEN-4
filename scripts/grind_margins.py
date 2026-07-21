import sys
import os
import json
from dataclasses import dataclass
from typing import List, Callable, Any
from config.system_config import SystemConfig
from digital_twin.network_1d import Network1DTwin
from validation.gates import Verdict, GateResult
from physics.base import NonPhysicalStateError

@dataclass
class FailureMode:
    component: str
    stressor_name: str
    nominal_val: float
    step_val: float
    apply_stressor: Callable[[Any, float], None]
    is_failed: Callable[[Any, List[GateResult]], bool]

def run_twin_to_steady_state(twin: Network1DTwin, max_time: float = 0.05, dt: float = 0.01) -> List[GateResult]:
    # Use the real gates
    from validation.gates import ALL_GATES
    from physics.base import ValidationError
    gates = [g(twin.config) for g in ALL_GATES]
    
    try:
        # Step through time
        t = 0
        while t < max_time:
            twin.run(dt)
            t += dt
    except NonPhysicalStateError:
        pass
    except ValidationError:
        pass
    except Exception:
        pass
        
    results = []
    for g in gates:
        res = g.execute(twin)
        results.append(res)
    return results

def run_grinder():
    print("Running Grinder Engine...")
    config = SystemConfig()
    
    # 1. Registry
    registry: List[FailureMode] = []
    
    # Hook up accumulator
    def apply_accum_stressor(twin, val):
        if hasattr(twin, 'fross'):
            twin.fross.injected_pulse = val
            
    def check_accum_failure(twin, results):
        # Failed if NonPhysicalStateError was caught (V_gas <= 0 -> pressure -> inf)
        # or if Gate3_FROSS4Transient fails
        for r in results:
            if r.gate_id == "G3" and r.verdict == Verdict.FAIL:
                return True
            if r.verdict == Verdict.INDETERMINATE and "Non-physical" in str(r.reason):
                return True
        # also check twin state manually if V_accum <= 0
        if twin.state.V_accum <= 1e-12: # our envelope
            return True
        return False
        
    registry.append(FailureMode(
        component="Accumulator",
        stressor_name="injected_pulse",
        nominal_val=0.0,
        step_val=1e5,
        apply_stressor=apply_accum_stressor,
        is_failed=check_accum_failure
    ))
    
    report_lines = [
        "# Margin Report",
        "",
        "| Component | Stressor | Failure Criterion | Threshold Value | Margin vs Nominal |",
        "|---|---|---|---|---|"
    ]
    
    for mode in registry:
        print(f"Stressing {mode.component} via {mode.stressor_name}...")
        
        # Nominal
        val = mode.nominal_val
        margin = 0.0
        
        while True:
            twin = Network1DTwin(config)
            twin.state = twin.state.model_copy(update={'p_vessel': config.accum_precharge})
            if hasattr(twin, 'fross') and hasattr(twin.fross, 'accumulator'):
                twin.fross.accumulator.params.beta_oil = 1.0
            mode.apply_stressor(twin, val)
            
            try:
                results = run_twin_to_steady_state(twin)
                failed = mode.is_failed(twin, results)
            except NonPhysicalStateError:
                failed = True
            except ValidationError:
                failed = True
            except Exception:
                failed = True
                
            if failed:
                print(f"  -> Failed at {val}")
                margin = val - mode.nominal_val
                report_lines.append(f"| {mode.component} | {mode.stressor_name} | V_gas<=0 / G3 FAIL | {val} | {margin} |")
                break
                
            val += mode.step_val
            if val > 1e9: # safety breakout
                report_lines.append(f"| {mode.component} | {mode.stressor_name} | Unknown | >1e9 | >1e9 |")
                break

    report_path = "Margin_Report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    run_grinder()

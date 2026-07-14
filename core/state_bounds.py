import time
from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum, auto

class SafetyAction(Enum):
    ARMED = auto()
    WARNING = auto()
    FAULT_LATCH = auto()
    EMERGENCY_DUMP = auto()

@dataclass(frozen=True)
class SafetyEvent:
    timestamp_ns: int
    source_module: str
    bound_violated: str
    value: float
    limit: float
    state_snapshot: Any  # StateVector reference

# Hard-coded absolute limits (Whitepaper §13.1)
SAFETY_BOUNDS = {
    "T_core": {
        "max": 3695.0,
        "action": SafetyAction.FAULT_LATCH,
        "reason": "ELECTRODE_MELTDOWN",
    },
    "p_vessel": {
        "max": 0.90 * 5.0e6,
        "action": SafetyAction.FAULT_LATCH,
        "reason": "VESSEL_OVERPRESSURE",
    },
    "omega": {
        "max": 6000.0 * 2.0 * 3.141592653589793 / 60.0,  # 628.3 rad/s
        "action": SafetyAction.FAULT_LATCH,
        "reason": "OVERSPEED",
    },
    "V_accum": {
        "min": 1.0e-6,
        "action": SafetyAction.WARNING,
        "reason": "ACCUMULATOR_NEAR_EMPTY",
    },
}

def check_bounds(state) -> Optional[SafetyEvent]:
    """
    Fast O(1) safety boundary check.
    Returns SafetyEvent on first violation, None if safe.
    """
    # Temperature check
    if state.T_core > SAFETY_BOUNDS["T_core"]["max"]:
        return SafetyEvent(
            timestamp_ns=time.time_ns(),
            source_module="state_bounds",
            bound_violated="T_core",
            value=state.T_core,
            limit=SAFETY_BOUNDS["T_core"]["max"],
            state_snapshot=state,
        )
    
    # Pressure check
    if state.p_vessel > SAFETY_BOUNDS["p_vessel"]["max"]:
        return SafetyEvent(
            timestamp_ns=time.time_ns(),
            source_module="state_bounds",
            bound_violated="p_vessel",
            value=state.p_vessel,
            limit=SAFETY_BOUNDS["p_vessel"]["max"],
            state_snapshot=state,
        )
    
    # RPM check
    omega_max = SAFETY_BOUNDS["omega"]["max"]
    if state.omega > omega_max:
        return SafetyEvent(
            timestamp_ns=time.time_ns(),
            source_module="state_bounds",
            bound_violated="omega",
            value=state.omega,
            limit=omega_max,
            state_snapshot=state,
        )
    
    # Accumulator minimum
    if state.V_accum < SAFETY_BOUNDS["V_accum"]["min"]:
        return SafetyEvent(
            timestamp_ns=time.time_ns(),
            source_module="state_bounds",
            bound_violated="V_accum",
            value=state.V_accum,
            limit=SAFETY_BOUNDS["V_accum"]["min"],
            state_snapshot=state,
        )
    
    return None

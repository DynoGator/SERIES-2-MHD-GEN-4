from enum import Enum, auto
from typing import List, Optional
from collections import deque
from core.state_bounds import SafetyEvent, SafetyAction

class SafetyState(Enum):
    ARMED = auto()
    WARNING = auto()
    FAULT_LATCH = auto()
    EMERGENCY_DUMP = auto()

class SafetyMachine:
    """
    Deterministic FAULT_LATCH state machine.
    No self-clear. Requires explicit two-step reset.
    """
    def __init__(self, max_history: int = 10000):
        self._state = SafetyState.ARMED
        self._history: deque = deque(maxlen=max_history)
        self._reset_ack_1 = False
        self._reset_ack_2 = False
        self._investigation_complete = False
    
    @property
    def state(self) -> SafetyState:
        return self._state
    
    def process_event(self, event: SafetyEvent) -> SafetyState:
        """Process incoming safety event. Idempotent if already latched."""
        if self._state == SafetyState.FAULT_LATCH:
            return self._state
        
        self._history.append(event)
        
        if event.bound_violated in ("T_core", "p_vessel", "omega"):
            self._state = SafetyState.FAULT_LATCH
        elif event.bound_violated == "V_accum":
            self._state = SafetyState.WARNING
        
        return self._state
    
    def reset(self, ack_1: bool, ack_2: bool, investigation: bool) -> bool:
        """
        Attempt reset from FAULT_LATCH to ARMED.
        Requires two-step acknowledgment + investigation flag.
        Returns True if reset succeeded.
        """
        if self._state != SafetyState.FAULT_LATCH:
            return False
        
        if ack_1 and ack_2 and investigation:
            self._state = SafetyState.ARMED
            self._reset_ack_1 = False
            self._reset_ack_2 = False
            self._investigation_complete = False
            return True
        
        self._reset_ack_1 = ack_1
        self._reset_ack_2 = ack_2
        self._investigation_complete = investigation
        return False
    
    def get_history(self) -> List[SafetyEvent]:
        return list(self._history)

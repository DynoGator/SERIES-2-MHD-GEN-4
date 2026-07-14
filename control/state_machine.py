"""
Full 15-State Machine
"""
from enum import Enum
from config.system_config import SystemConfig

class TwinState(Enum):
    LOCKOUT = 0
    SAFE_IDLE = 1
    LEAK_TEST = 2
    COLD_CIRCULATION = 3
    MODAL_IDENTIFICATION = 4
    PREHEAT = 5
    SEED_ARM = 6
    PREIONIZE = 7
    FIELD_RAMP = 8
    MHD_OPEN_CIRCUIT = 9
    LOAD_RAMP = 10
    STEADY_OPERATION = 11
    CONTROLLED_SHUTDOWN = 12
    FAST_SHUTDOWN = 13
    FAULT_LATCH = 14

class StateEvent(Enum):
    MAINTENANCE_KEY_TRUE = 1
    SENSORS_NOMINAL = 2
    PRESSURE_DECAY_OK = 3
    COMPRESSOR_MAP_OK = 4
    MODES_IDENTIFIED = 5
    LINER_TEMP_OK = 6
    SEED_SYSTEM_PERMISSIVE = 7
    PLASMA_IMPEDANCE_OK = 8
    B_FIELD_STABLE = 9
    OPEN_CIRCUIT_VOLTAGE_OK = 10
    SEGMENTS_LOADED_BALANCED = 11
    SAFETY_FAULT = 12
    RESET_ACK_1 = 13
    RESET_ACK_2 = 14
    INVESTIGATION_COMPLETE = 15
    SHUTDOWN_REQUEST = 16

class TwinStateMachine:
    def __init__(self, config: SystemConfig):
        self.config = config
        self._state = TwinState.LOCKOUT
        self._reset_ack_1 = False
        self._reset_ack_2 = False
        self._investigation_complete = False

    @property
    def current_state(self) -> TwinState:
        return self._state

    def reset(self) -> None:
        if self._state == TwinState.FAULT_LATCH:
            if self._reset_ack_1 and self._reset_ack_2 and self._investigation_complete:
                self._state = TwinState.LOCKOUT
                self._reset_ack_1 = False
                self._reset_ack_2 = False
                self._investigation_complete = False

    def trigger_reset_flags(self, ack1: bool, ack2: bool, inv: bool):
        self._reset_ack_1 = ack1
        self._reset_ack_2 = ack2
        self._investigation_complete = inv

    def transition(self, event: StateEvent) -> TwinState:
        if event == StateEvent.SAFETY_FAULT:
            self._state = TwinState.FAULT_LATCH
            return self._state

        if self._state == TwinState.FAULT_LATCH:
            return self._state

        if self._state == TwinState.LOCKOUT and event == StateEvent.MAINTENANCE_KEY_TRUE:
            self._state = TwinState.SAFE_IDLE
        elif self._state == TwinState.SAFE_IDLE and event == StateEvent.SENSORS_NOMINAL:
            self._state = TwinState.LEAK_TEST
        elif self._state == TwinState.LEAK_TEST and event == StateEvent.PRESSURE_DECAY_OK:
            self._state = TwinState.COLD_CIRCULATION
        elif self._state == TwinState.COLD_CIRCULATION and event == StateEvent.COMPRESSOR_MAP_OK:
            self._state = TwinState.MODAL_IDENTIFICATION
        elif self._state == TwinState.MODAL_IDENTIFICATION and event == StateEvent.MODES_IDENTIFIED:
            self._state = TwinState.PREHEAT
        elif self._state == TwinState.PREHEAT and event == StateEvent.LINER_TEMP_OK:
            self._state = TwinState.SEED_ARM
        elif self._state == TwinState.SEED_ARM and event == StateEvent.SEED_SYSTEM_PERMISSIVE:
            self._state = TwinState.PREIONIZE
        elif self._state == TwinState.PREIONIZE and event == StateEvent.PLASMA_IMPEDANCE_OK:
            self._state = TwinState.FIELD_RAMP
        elif self._state == TwinState.FIELD_RAMP and event == StateEvent.B_FIELD_STABLE:
            self._state = TwinState.MHD_OPEN_CIRCUIT
        elif self._state == TwinState.MHD_OPEN_CIRCUIT and event == StateEvent.OPEN_CIRCUIT_VOLTAGE_OK:
            self._state = TwinState.LOAD_RAMP
        elif self._state == TwinState.LOAD_RAMP and event == StateEvent.SEGMENTS_LOADED_BALANCED:
            self._state = TwinState.STEADY_OPERATION
        elif self._state == TwinState.STEADY_OPERATION and event == StateEvent.SHUTDOWN_REQUEST:
            self._state = TwinState.CONTROLLED_SHUTDOWN
        
        return self._state

    def can_transition(self, from_state: TwinState, to_state: TwinState) -> bool:
        pass

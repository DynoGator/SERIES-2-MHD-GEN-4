import pytest
from control.state_machine import TwinStateMachine, TwinState, StateEvent
from config.system_config import SystemConfig

def test_no_self_clear():
    config = SystemConfig()
    sm = TwinStateMachine(config)
    sm.transition(StateEvent.SAFETY_FAULT)
    assert sm.current_state == TwinState.FAULT_LATCH
    
    sm.transition(StateEvent.SENSORS_NOMINAL)
    assert sm.current_state == TwinState.FAULT_LATCH

def test_nominal_startup_sequence():
    config = SystemConfig()
    sm = TwinStateMachine(config)
    
    sequence = [
        (StateEvent.MAINTENANCE_KEY_TRUE, TwinState.SAFE_IDLE),
        (StateEvent.SENSORS_NOMINAL, TwinState.LEAK_TEST),
        (StateEvent.PRESSURE_DECAY_OK, TwinState.COLD_CIRCULATION),
        (StateEvent.COMPRESSOR_MAP_OK, TwinState.MODAL_IDENTIFICATION),
        (StateEvent.MODES_IDENTIFIED, TwinState.PREHEAT),
        (StateEvent.LINER_TEMP_OK, TwinState.SEED_ARM),
        (StateEvent.SEED_SYSTEM_PERMISSIVE, TwinState.PREIONIZE),
        (StateEvent.PLASMA_IMPEDANCE_OK, TwinState.FIELD_RAMP),
        (StateEvent.B_FIELD_STABLE, TwinState.MHD_OPEN_CIRCUIT),
        (StateEvent.OPEN_CIRCUIT_VOLTAGE_OK, TwinState.LOAD_RAMP),
        (StateEvent.SEGMENTS_LOADED_BALANCED, TwinState.STEADY_OPERATION)
    ]
    
    for event, expected_state in sequence:
        assert sm.transition(event) == expected_state
        assert sm.current_state == expected_state

def test_fault_from_any_state():
    for state in TwinState:
        config = SystemConfig()
        sm = TwinStateMachine(config)
        sm._state = state
        sm.transition(StateEvent.SAFETY_FAULT)
        assert sm.current_state == TwinState.FAULT_LATCH

def test_reset_requires_two_step():
    config = SystemConfig()
    sm = TwinStateMachine(config)
    sm.transition(StateEvent.SAFETY_FAULT)
    
    sm.trigger_reset_flags(True, False, False)
    sm.reset()
    assert sm.current_state == TwinState.FAULT_LATCH
    
    sm.trigger_reset_flags(True, True, False)
    sm.reset()
    assert sm.current_state == TwinState.FAULT_LATCH
    
    sm.trigger_reset_flags(True, True, True)
    sm.reset()
    assert sm.current_state == TwinState.LOCKOUT

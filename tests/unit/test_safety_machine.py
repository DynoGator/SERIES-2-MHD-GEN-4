import time
from core.safety_machine import SafetyMachine, SafetyState
from core.state_bounds import SafetyEvent
from core.state_vector import StateVector

def test_no_self_clear():
    sm = SafetyMachine()
    state = StateVector(theta=0.0, omega=10.0, T_core=4000.0, p_vessel=1e5, V_accum=0.1)
    ev = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="T_core",
        value=4000.0,
        limit=3695.0,
        state_snapshot=state
    )
    sm.process_event(ev)
    assert sm.state == SafetyState.FAULT_LATCH
    
    # Try reset without acks
    success = sm.reset(False, False, False)
    assert not success
    assert sm.state == SafetyState.FAULT_LATCH

def test_two_step_reset():
    sm = SafetyMachine()
    state = StateVector(theta=0.0, omega=10.0, T_core=4000.0, p_vessel=1e5, V_accum=0.1)
    ev = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="T_core",
        value=4000.0,
        limit=3695.0,
        state_snapshot=state
    )
    sm.process_event(ev)
    assert sm.state == SafetyState.FAULT_LATCH
    
    success = sm.reset(True, True, True)
    assert success
    assert sm.state == SafetyState.ARMED

def test_history_logged():
    sm = SafetyMachine()
    state = StateVector(theta=0.0, omega=10.0, T_core=1000.0, p_vessel=1e5, V_accum=0.1)
    ev1 = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="V_accum",
        value=1e-7,
        limit=1e-6,
        state_snapshot=state
    )
    ev2 = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="T_core",
        value=4000.0,
        limit=3695.0,
        state_snapshot=state
    )
    sm.process_event(ev1)
    sm.process_event(ev2)
    assert len(sm.get_history()) == 2

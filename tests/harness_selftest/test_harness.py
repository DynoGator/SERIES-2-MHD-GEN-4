import pytest
from validation.gates import GateResult, Verdict
from control.state_machine import TwinStateMachine, TwinState, StateEvent
from core.safety_machine import SafetyMachine, SafetyState
from core.state_bounds import SafetyEvent
import time

def test_gate_result_stores_indeterminate():
    res = GateResult("G0", Verdict.INDETERMINATE, {}, {}, "", "test reason")
    assert res.verdict == Verdict.INDETERMINATE
    assert res.reason == "test reason"

def test_gate_result_stores_fail_and_reason():
    res = GateResult("G1", Verdict.FAIL, {"val": 10.0}, {"limit": False}, "", "Value exceeded limit")
    assert res.verdict == Verdict.FAIL
    assert res.reason == "Value exceeded limit"
    assert res.measured_values["val"] == 10.0

def test_gate_result_stores_pass_without_reason():
    res = GateResult("G2", Verdict.PASS, {"val": 5.0}, {"limit": True}, "", None)
    assert res.verdict == Verdict.PASS
    assert res.reason is None

def test_state_machine_fault_latch_from_safety_fault():
    # We mock config as None since TwinStateMachine doesn't use it heavily in transition
    sm = TwinStateMachine(None)
    assert sm.current_state == TwinState.LOCKOUT
    sm.transition(StateEvent.SAFETY_FAULT)
    assert sm.current_state == TwinState.FAULT_LATCH

def test_state_machine_cannot_escape_fault_latch_without_reset():
    sm = TwinStateMachine(None)
    sm.transition(StateEvent.SAFETY_FAULT)
    # Try transitioning to something else
    sm.transition(StateEvent.MAINTENANCE_KEY_TRUE)
    assert sm.current_state == TwinState.FAULT_LATCH

def test_safety_machine_enters_warning_on_accum_depletion():
    sm = SafetyMachine()
    event = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="V_accum",
        value=0.0,
        limit=1e-6,
        state_snapshot=None
    )
    sm.process_event(event)
    assert sm.state == SafetyState.WARNING

def test_safety_machine_enters_fault_latch_on_pressure():
    sm = SafetyMachine()
    event = SafetyEvent(
        timestamp_ns=time.time_ns(),
        source_module="test",
        bound_violated="p_vessel",
        value=1e7,
        limit=5e6,
        state_snapshot=None
    )
    sm.process_event(event)
    assert sm.state == SafetyState.FAULT_LATCH

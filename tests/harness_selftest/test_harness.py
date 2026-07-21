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
            reason="ACCUMULATOR_NEAR_EMPTY",
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
        reason="VESSEL_OVERPRESSURE",
        state_snapshot=None
    )
    sm.process_event(event)
    assert sm.state == SafetyState.FAULT_LATCH

# Falsification Fixtures

from digital_twin.lumped_model import LumpedDigitalTwin
from config.system_config import SystemConfig
from physics.base import IntegrationDivergedError, NonPhysicalStateError
from core.state_vector import StateVector
from validation.gates import ValidationGate

class MockGenerationGate(ValidationGate):
    def execute(self, twin):
        err = self._run_twin_safely(twin, 0.1, "GMock1")
        if err: return err
        # Mock check: did we generate anything?
        # If sigma == 0, we can't generate power.
        gen = 0.0 # Suppose we read from twin
        if getattr(twin, "mock_sigma", 1.0) == 0.0:
            return GateResult("GMock1", Verdict.FAIL, {"gen": 0.0}, {"gen_gt_0": False}, "", "no conductivity")
        return GateResult("GMock1", Verdict.PASS, {"gen": 1.0}, {"gen_gt_0": True}, "", None)
    def criteria(self): return {}

def test_sigma_zero_fails_generation_gate():
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    twin.mock_sigma = 0.0
    gate = MockGenerationGate(config)
    res = gate.execute(twin)
    assert res.verdict == Verdict.FAIL
    assert "no conductivity" in res.reason

class MockEnergyGate(ValidationGate):
    def execute(self, twin):
        # hand compute
        w_net = getattr(twin, "mock_w_net", 100.0)
        x_source = getattr(twin, "mock_x_source", 50.0)
        if w_net > x_source:
            imbalance = w_net - x_source
            return GateResult("GMock2", Verdict.FAIL, {"imbalance": imbalance}, {"w_lt_x": False}, "", f"W_net > X_source by {imbalance}")
        return GateResult("GMock2", Verdict.PASS, {}, {}, "", None)
    def criteria(self): return {}

def test_w_net_gt_x_source_fails_energy_gate():
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    twin.mock_w_net = 100.0
    twin.mock_x_source = 50.0
    gate = MockEnergyGate(config)
    res = gate.execute(twin)
    assert res.verdict == Verdict.FAIL
    assert res.measured_values["imbalance"] == 50.0

class DivergentTwin(LumpedDigitalTwin):
    def run(self, dt):
        raise IntegrationDivergedError("diverged step")

def test_divergent_dydt_indeterminate():
    config = SystemConfig()
    twin = DivergentTwin(config)
    gate = MockGenerationGate(config)
    res = gate.execute(twin)
    assert res.verdict == Verdict.INDETERMINATE
    assert "Integration Diverged" in res.reason

class NonPhysicalTwin(LumpedDigitalTwin):
    def run(self, dt):
        # T_core < 0
        raise NonPhysicalStateError("T_core<=0")

def test_t_core_lt_zero_indeterminate():
    config = SystemConfig()
    twin = NonPhysicalTwin(config)
    gate = MockGenerationGate(config)
    res = gate.execute(twin)
    assert res.verdict == Verdict.INDETERMINATE
    assert "Non-physical state during run: T_core<=0" in res.reason

def test_t_core_meltdown_fault_latch():
    # End-to-end check
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    # Inject 3695.1
    twin.state = twin.state.evolve(T_core=3696.0)
    twin.run(0.1)
    assert twin.safety_machine.state == SafetyState.FAULT_LATCH
    assert twin.safety_machine.get_history()[-1].reason == "ELECTRODE_MELTDOWN"

class MissingMetricGate(ValidationGate):
    def execute(self, twin):
        # We need 'temperature' but it's not provided
        metric = getattr(twin, "mock_missing_metric", None)
        if metric is None:
            return GateResult("GMock3", Verdict.INDETERMINATE, {}, {}, "", "missing metric: temperature")
        return GateResult("GMock3", Verdict.PASS, {}, {}, "", None)
    def criteria(self): return {}

def test_missing_metric_indeterminate():
    config = SystemConfig()
    twin = LumpedDigitalTwin(config)
    gate = MissingMetricGate(config)
    res = gate.execute(twin)
    assert res.verdict == Verdict.INDETERMINATE
    assert "missing metric: temperature" in res.reason

def test_round_trip_invariant():
    s = StateVector(theta=1.0, omega=2.0, T_core=3000.0, p_vessel=1e5, V_accum=0.5, m_seed=0.1, T_electron=500.0, coherence_r=0.9)
    assert StateVector.from_array(s.to_array(has_segments=False), has_segments=False) == s
    
    import numpy as np
    s_seg = StateVector(theta=1.0, omega=2.0, T_core=3000.0, p_vessel=1e5, V_accum=0.5, m_seed=0.1, T_electron=500.0, coherence_r=0.9, segment_currents=np.ones(8), segment_voltages=np.full(8, 2.0))
    s2 = StateVector.from_array(s_seg.to_array(has_segments=True), has_segments=True)
    # check equality manually because arrays in BaseModel == is sometimes tricky
    assert s2.theta == s_seg.theta
    assert s2.omega == s_seg.omega
    assert np.allclose(s2.segment_currents, s_seg.segment_currents)
    assert np.allclose(s2.segment_voltages, s_seg.segment_voltages)


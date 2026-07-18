import pytest
from rehearsal.scenario import ScenarioEngine

def test_gates_execute_in_order():
    engine = ScenarioEngine()
    results = engine.run()
    gate_names = [r.gate for r in results]
    assert tuple(gate_names) == ScenarioEngine.GATES

def test_full_mission_success():
    engine = ScenarioEngine()
    engine.run()
    assert engine.mission_status == "SUCCESS"
    for r in engine.results:
        assert r.verdict == "PASS"

def test_abort_on_gate_failure():
    engine = ScenarioEngine()
    engine._force_gpsdo_fail = True
    results = engine.run()
    
    assert engine.mission_status == "ABORTED"
    assert any(r.gate == "GPSDO_LOCK" and r.verdict == "FAIL" for r in results)
    
    # Should not attempt later gates
    gate_names = [r.gate for r in results]
    assert "CALIBRATION" not in gate_names

def test_report_digest_deterministic():
    e1 = ScenarioEngine(seed=42)
    e2 = ScenarioEngine(seed=42)
    
    e1.run()
    e2.run()
    
    assert e1.digest == e2.digest

def test_failover_observed_in_mission():
    engine = ScenarioEngine()
    engine.run()
    
    restore_res = next(r for r in engine.results if r.gate == "BROKER_RESTORE")
    assert "BROKERED->MESH->BROKERED" in restore_res.detail
